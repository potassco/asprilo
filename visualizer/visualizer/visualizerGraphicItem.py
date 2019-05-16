from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QBrush
from . import modelView 
from . import visualizerItem
from .configuration import *

VIZ_STATE_MOVED     = 0x0001
VIZ_STATE_DELIVERED = 0x0002
VIZ_STATE_PICKED_UP = 0x0004
VIZ_STATE_PUT_DOWN  = 0x0008
VIZ_STATE_MOVE      = 0x0010
VIZ_STATE_DELIVER   = 0x0020
VIZ_STATE_PICK_UP   = 0x0040
VIZ_STATE_PUT_DOWN2 = 0x0080
VIZ_STATE_CHARGED   = 0x0100
VIZ_STATE_CHARGE    = 0x1000
VIZ_STATE_ACTION    = 0xffff

# This function iterates between two color values.
def calculate_color(first_color, second_color, multiplier):
    red = (min(first_color.red(), second_color.red()), 
            max(first_color.red(), second_color.red()))
    green = (min(first_color.green(), second_color.green()), 
            max(first_color.green(), second_color.green()))
    blue = (min(first_color.blue(), second_color.blue()), 
            max(first_color.blue(), second_color.blue()))
    return QColor(
                red[0] + (red[1] - red[0]) * multiplier,
                green[0] + (green[1] - green[0]) * multiplier,
                blue[0] + (blue[1] - blue[0]) * multiplier)

# This is the templete class for visualizer graphic items.
# There should never be an instance of this class.
# A visualizer graphic item is a part of the visualizer model
# that is drawn in on the model view and can perform actions.
# To add a new kind of graphic items create a child class
# of VisualizerGraphicItem in this file and add it in the 
# model.create_item function to the model. This is the only function 
# in the model that should be changed. The behaivor and values of the
# object should be defindes inside of its own class.
class VisualizerGraphicItem(QGraphicsItem, visualizerItem.VisualizerItem):
    def __init__(self, ID = '0', x = 0, y = 0):
        QGraphicsItem.__init__(self)
        visualizerItem.VisualizerItem.__init__(self)
        self._kind_name = ''
        self._id = ID
        self._model = None
        self._position = (x, y) 
        self._start_position = (x, y)
        self._dragged = None
        self._enable_drag = False
        # _graphics_item is the main graphic item of this object
        # and is used for some default functions
        self._graphics_item = None  
        # _text is a graphic item that is drawn 
        # on the model view and represents primarily the id of the item.
        self._text = None
        self._actions = []
        self._color = None
        self._colors = [QColor(0,0,0)]
        self._display_mode = 0
        self._draw_path = False
        self.setAcceptedMouseButtons(Qt.MouseButtons(1))
        self._state = 0x00
        self._highlighted = False

    # Sets the starting position of an item.
    def set_starting_position(self, x, y):
        self._start_position = (x, y)

    # Sets the current position of an item.
    def set_position(self, x, y):
        self._position = (x, y)

    # Sets a specific color of an item. An item can have
    # more than one color.
    def set_color(self, color, color_id = 0):
        while color_id >= len(self._colors):
            self._colors.append(QColor(0,0,0))
        self._colors[color_id] = color

    # Sets the rectangle that an item can use to draw things in.
    # This equals usually one field of the grid in the model view.
    # This function usually defines the appearance of an object
    # on the grid.
    def set_rect(self, rect):
        return

    # Sets the action for the specific time step.
    # Overrides existing actions at the time step but prints out
    # a warning since this should never happen.
    # [Parameter action] is the action that should be performed.
    # The action must be a clingo.Symbol object.
    # [Parameter time_step] is the time step at which the action
    # shold be performed. The time step must be a positive integer.
    def set_action(self, action, time_step):
        if time_step < 0:
            print(('Warning: invalid time step in occurs(object('
                    + str(self._kind_name) + ','
                    + str(self._ID) + '),' + str(action)
                    + ',' + str(time_step) + ')'))
            print('time step is less than 0')
            return
        for ii in range((time_step + 1) - len(self._actions)):
            self._actions.append(None)
        if not self._actions[time_step] == None:
            print(('Warning: for object(' + str(self._kind_name)
                    + ', ' + str(self._id)
                    + ') multiple actions are defined at time step '
                    + str(time_step)))
        self._actions[time_step] = action

    # Sets the current display mode.
    # This is set by the model view and determines whether
    # the object text should be rendered and whether the item 
    # should be rendered in the whole grid field.
    # It is primarily defined by the zoom factor and the grid size.
    def set_display_mode(self, display_mode):
        self._display_mode =  display_mode

    # Sets whether the path of the object should be drawn.
    # Should only be used for items that can have a path like robots.
    def set_draw_path(self, draw_path):
        self._draw_path = draw_path

    # This function handels the input phrases for every item.
    # This is called for every phrase the model receives with the
    # following syntax: 
    # init(object([object type], [object ID]), value([value name], [value])).
    # While [object type] is the same as self._kind_name and [object ID]
    # is the ID of the object and is the same as self._id.
    # The model decides based on this value the object the receives
    # the phrase.
    # [Parameter name] is the name of the value.
    # [value name] part of the phrase. It is represented by an instance 
    # of a clingo.Symbol object.
    # [Parameter value] is the actual value. It contains the [value]
    # part of the phrase. It is represented by an instance of a
    # clingo.Symbol object.
    # Returns 1 if the phrase cannot be parsed, -1 if one parameter is
    # invalid and 0 if the function succeeded.
    def parse_init_value(self, name, value):
        if value is None or name is None:
            return -1
        if name == 'at':
            pos = (value.arguments[0].number, value.arguments[1].number)
            self.set_starting_position(pos[0], pos[1])
            self.set_position(pos[0], pos[1])
            return 0
        return 1

    # Enables  and disables the drag and drop feature for the
    # model editor. This will be set by the model.
    # It will be set to false as soon as the first action
    # atom occurs.
    def enable_drag(self, enable):
        self._enable_drag = enable

    # Resets the object to its original values.
    # Sets an object to its starting position.
    def restart(self):
        self._position = self._start_position

    # Action handler. Must be implemented for items
    # which can perform actions. This function will be called
    # every time the model does one time step forward.
    def do_action(self, time_step):
        return

    # Reverse action handler. Must be implemented for items
    # which can perform actions. This function will be called 
    # every time the model does one time step backwards.
    def undo_action(self, time_step):
        return

    # Deletes all actions for an object.
    def clear_actions(self):
        self._actions = []

    # Converts the item to a string that represents the object.
    # This function is used to send the whole model to a solver
    # and to save a instance to a file.
    def to_init_str(self):
        return ('init(object('
                + self._kind_name + ','
                + str(self._id) + '), value(at,('
                + str(self._position[0]) + ','
                + str(self._position[1]) + '))).')

    # This function returns a list of strings that represents all
    # actions of an item.
    def to_occurs_str(self):
        actions = []
        count = 0
        for action in self._actions:
            if action is None:
                actions.append(None)
            else:
                actions.append('occurs(object('
                    + self._kind_name + ', '
                    + str(self._id) + '), '
                    + str(action) + ', '
                    + str(count) + ')')
            count = count + 1
        return actions

    # Determines the color of an item dependent on his number.
    def determine_color(self, number, count, pattern = None):
        return

    # Returns the name of the item.
    def get_name(self):
        return self._kind_name

    # Return the position of an item.
    def get_position(self):
        return self._position

    # Returns a specific color of an item.
    def get_color(self, color_id):
        if color_id < len(self._colors):
            return self._colors[color_id]
        return None

    # Returns the current color of an item.
    def get_color(self):
        return self._color

    # Returns the current rectangle of an item.
    def get_rect(self):
        return None

    # Returns the action at a specific time step.
    # Returns None if no action is defined for this time step.
    def get_action(self, time_step):
        if time_step >= len(self._actions):
            return None  #break, if no action is defined
        if self._actions[time_step] == None:
            return None  #break, if no action is defined     
        return self._actions[time_step]   

    # Returns the current state of the item.
    def get_state(self):
        return self._state

    # Returns whether the path of this item should be drawn.
    def get_draw_path(self):
        return self._draw_path

    # Sets a new starting position and new current position for an 
    # item. If an item of the same kind is already on the same position
    # they swap positions. This function is used to edit instances with
    # the drag and drop feature.
    def edit_position_to(self, x, y):
        if (x, y) == self._position:
            return
        item2 = self._model.filter_items(item_kind = self._kind_name,
                                        position = (x,y),
                                        return_first = True)[0]
        if item2 is not None:
            item2.set_position(self._position[0], self._position[1])
            item2.set_starting_position(
                self._position[0], 
                self._position[1])
        self.set_position(x,y)
        self.set_starting_position(x, y)

    # This is a overridden QT function and used for drag and drop.
    def boundingRect(self):
        return self._graphics_item.boundingRect()

    def paint(self, painter, option, widget):
        return self._graphics_item.paint(painter, option, widget)

    # This is a overridden QT function and used for drag and drop.
    def mousePressEvent(self, event):
        if self._enable_drag:
            rect = self.get_rect()
            self._dragged = (event.scenePos().x(),
                             event.scenePos().y())
        event.accept()

    # This is a overridden QT function and used for drag and drop.
    def mouseReleaseEvent(self, event):
        model_view = None
        if self._dragged is not None:
            self._dragged = None
            for view in self.scene().views():
                if isinstance(view, modelView.ModelView):
                    model_view = view
        if model_view is None:
            return
        node = model_view.scene_coordinates_to_node(event.scenePos().x(),
                                                    event.scenePos().y())
        self.setPos(0, 0)

        if node is not None:
            self.edit_position_to(node[0], node[1])
        model_view.update()
        event.accept()

    # This is a overridden QT function and used for drag and drop.
    def mouseMoveEvent(self, event):
        if self._dragged is None:
            return
        self.setPos(event.scenePos().x() - self._dragged[0], 
                    event.scenePos().y() - self._dragged[1])
        event.accept()

    # Sets whether this item should be highlighted.
    # Highlighted items are be drawn lager.
    def set_highlighted(self, highlighted):
        self._highlighted = highlighted

# This class represents a picking station.
class PickingStation(VisualizerGraphicItem):
    def __init__(self, ID = 0, x = 0, y = 0):
        super(PickingStation, self).__init__(ID, x, y)
        self._kind_name = 'pickingStation'
        self._short_name = 'P'

        self._items = []
        self._graphics_item = QGraphicsRectItem(self)
        self._items.append(QGraphicsRectItem(self._graphics_item))
        self._items.append(QGraphicsRectItem(self._graphics_item))
        self._text = QGraphicsTextItem(self._graphics_item)

    # Sets the rectangle that a picking station can use to draw 
    # things in. This equals one field of the grid in the model view.
    # This function defines the appearance of the picking station
    # on the grid.
    def set_rect(self, rect):
        scale = config.get('display', 'id_font_scale')
        bold = config.get('display', 'id_font_bold')
        self._text.setFont(QFont('', rect.width()*0.08*scale))
        self._text.setPos(rect.x(), rect.y() + 0.6*rect.height())
        self._text.setDefaultTextColor(
            QColor(config.get('display', 'id_font_color')))
        if self._display_mode == 0:
            if bold:
                self._text.setHtml(
                    '<b>' + self._short_name +'(' + str(self._id) + ')</b>')
            else:
                self._text.setHtml(
                    self._short_name + '(' + str(self._id) + ')')
            self._graphics_item.setRect(
                rect.x(), rect.y(), 
                rect.width(), rect.height())
            self._items[0].setRect(
                rect.x() + rect.width()/5, rect.y(), 
                rect.width()/5, rect.height())
            self._items[1].setRect(
                rect.x() + rect.width()/5 * 3, rect.y(), 
                rect.width()/5, rect.height())
        elif self._display_mode == 1:
            self._text.setPlainText('')
            self._graphics_item.setRect(
                rect.x(), rect.y(), rect.width(), rect.height())
            self._items[0].setRect(
                rect.x() + rect.width()/5, rect.y(), 
                rect.width()/5, rect.height())
            self._items[1].setRect(
                rect.x() + rect.width()/5 * 3, rect.y(), 
                rect.width()/5, rect.height())            

    # Determines the color of the picking station.   
    def determine_color(self, number, count, pattern = None):
        color = self._colors[0]
        color2 = self._colors[1]
        color.setAlpha(150)
        color2.setAlpha(150)
        brush = QBrush(color)
        brush2 = QBrush(color2)

        self._graphics_item.setBrush(brush)
        self._items[0].setBrush(brush2)
        self._items[1].setBrush(brush2)

    # Returns the current rectangle of the picking station.
    def get_rect(self):
        return self._graphics_item.rect()

    # This class represents a charging station.
    # It is the same as a picking station except of the name.
class ChargingStation(PickingStation):
    def __init__(self, ID = 0, x = 0, y = 0):
        super(ChargingStation, self).__init__(ID, x, y)
        self._kind_name = 'chargingStation'
        self._short_name = 'C'

    # This class represents a shelf.    
class Shelf(VisualizerGraphicItem):
    def __init__(self, ID = 0, x = 0, y = 0):
        super(self.__class__, self).__init__(ID, x, y)
        self._kind_name = 'shelf'
        self._carried = None
        # _products is a list of product. Every product is a triple.
        # (product id, product amount, removed product amount)
        self._products   = []
        self._graphics_item = QGraphicsEllipseItem(self)
        self._graphics_carried = QGraphicsEllipseItem()
        self._text = QGraphicsTextItem(self)
        self.setZValue(2.0)
        self.update_tooltip()

    # Sets the rectangle that a shelf can use to draw things in.
    # This equals one field of the grid in the model view.
    # This function defines the appearance of the shelf
    # on the grid.
    def set_rect(self, rect):
        if self._carried is not None:
            rect = self._carried.get_rect()

        scale = config.get('display', 'id_font_scale')
        bold = config.get('display', 'id_font_bold')
        self._text.setFont(QFont('', rect.width()*0.08*scale))
        self._text.setPos(rect.x(), rect.y() + 0.4*rect.height())
        self._text.setDefaultTextColor(
            QColor(config.get('display', 'id_font_color')))

        if self._display_mode == 0:
            if bold:
                self._text.setHtml('<b>S(' + str(self._id) + ')</b>')
            else:
                self._text.setHtml('S(' + str(self._id) + ')')
            self._graphics_item.setRect(rect.x() + 0.25*rect.width(), 
                                        rect.y() + 0.25*rect.height(),
                                        rect.width()*0.5,
                                        rect.height()*0.5)

            self._graphics_carried.setRect(rect.x() + 0.325*rect.width(), 
                                        rect.y() + 0.325*rect.height(),
                                        rect.width()*0.35,
                                        rect.height()*0.35)
        elif self._display_mode == 1:
            self._text.setPlainText('')
            self._graphics_item.setRect(rect.x() + 0.05*rect.width(),
                                        rect.y() + 0.05*rect.height(),
                                        rect.width()*0.9,
                                        rect.height()*0.9)
            self._graphics_carried.setRect(rect.x() + 0.125*rect.width(),
                                        rect.y() + 0.125*rect.height(),
                                        rect.width()*0.75,
                                        rect.height()*0.75)

    # Sets the robot that carries this shelf at the current time step.
    # Sets also the shelf that is carried by the robot to this.
    # If the shelf is already carried by another robot the carried 
    # shelf of this robot will be set to None.
    def set_carried(self, robot):
        #Checks if the shelf is already carried by the robot 
        #to prevent a infinite loop.
        if robot == self._carried:
            return
        temp = self._carried
        self._carried = robot
        if temp is not None:
            temp.set_carries(None)
        if self._carried is not None:
            self._graphics_carried.setParentItem(self._graphics_item)
            self._carried.set_carries(self)
        else:
            self._graphics_carried.setParentItem(None)

    # Reset the products in the shelf.
    # Sets the shelf to its starting position.
    def restart(self):
        super(self.__class__, self).restart()
        products = []
        for product in self._products:
            products.append((product[0], product[1], 0))
        self._products = products

    # Converts the shelf to a string that represents the shelf.
    # This function is used to send shelves to a solver
    # and to save shelves to a file.
    def to_init_str(self):
        s = super(self.__class__, self).to_init_str()
        for product in self._products:
            s += ('init(object(product,' 
                    + str(product[0]) + '),value(on,('
                    + str(self._id) + ',' 
                    + str(product[1]) + '))).')
        return s

    # Updates the tooltip for the shelf.
    def update_tooltip(self):
        tooltip = "shelf(" + str(self._id) + ")\nproducts:\n"
        for product in self._products:
            tooltip = tooltip + str(product) + "\n"
        self.setToolTip(tooltip)

    # Returns a product with the given product id.
    # If no product with the given id is on the shelf it returns None.
    def find_product(self, product_id):
        for product in self._products:
            if str(product_id) == str(product[0]):
                return product
        return None

    # Sets the carried amount of a product on this shelf.
    # If the shelf already contains products with the 
    # given id the amount of products will be overriden.
    def set_product_amount(self, product_id, amount):
        product = self.find_product(product_id)
        if product is None:
            self._products.append((product_id, amount, 0))
        else:
            self._products.remove(product)
            self._products.append((product_id, amount, product[2]))
        self.update_tooltip()

    # Adds to the carried amount of a product on this shelf.
    # If amount is 0 and the shelf already contains products
    # with the given amount it will be set to 0.
    def add_product(self, product_id, amount):
        product = self.find_product(product_id)
        if product is None:
            self._products.append((product_id, amount, 0))
        else: 
            if amount == 0:
                self._products.append((product_id, 0, 0))
            else:
                self._products.append((product_id, product[1] + amount, 0))
            self._products.remove(product)
        self.update_tooltip()

    # Increases the removed amount counter of a product on the shelf.
    # If the shelf does not contain a product with the 
    # given id nothing happens.
    def remove_product(self, product_id, amount):
        product = self.find_product(product_id)
        if product is not None:
            self._products.append((product_id, product[1], product[2] + amount))
            self._products.remove(product)

    # Deletes a product from a shelf.
    # If the shelf does not contain a product with the 
    # given id nothing happens.
    def delete_product(self, product_id):
        product = self.find_product(product_id)
        if product is not None:
            self._products.remove(product)
        self.update_tooltip()

    # Determines the color of the picking station.
    def determine_color(self, number, count, pattern = None):
        color = calculate_color(self._colors[0], self._colors[1], (float)(number)/count)
        brush = QBrush(color)
        self._graphics_item.setBrush(brush)
        self._graphics_carried.setBrush(QBrush(self._colors[2]))

    # Returns the current amount of a specific product on a shelf.
    def get_product_amount(self, product_id):
        product = self.find_product(product_id)
        if product is None:
            return 0
        return product[1] - product[2]

    # Returns the current rectangle of the shelf.
    def get_rect(self):
        if self._display_mode == 0:
            rect = self._graphics_item.rect()
            width = rect.width()*2
            height = rect.height()*2
            rect.setLeft(rect.x() - 0.25*width)
            rect.setTop(rect.y() - 0.25*height)
            rect.setWidth(width)
            rect.setHeight(height)
            return rect
        elif self._display_mode == 1:
            rect = self._graphics_item.rect()
            width = rect.width()/0.9
            height = rect.height()/0.9
            rect.setLeft(rect.x() - 0.05*width)
            rect.setTop(rect.y() - 0.05*height)
            rect.setWidth(width)
            rect.setHeight(height)
            return rect

    # Returns the robot that carries the shelf at the current 
    # time step. This can be None.
    def get_carried(self):
        return self._carried

    # Iterates through every product on the shelf.
    def iterate_products(self):
        for product in self._products:
            yield product

    # Sets a new starting position and new current position for the 
    # shelf. If another shelf is already on the same position
    # they swap positions. This function is used to edit instances with
    # the drag and drop feature. Only shelf that are currently not carried 
    # can be moved.
    def edit_position_to(self, x, y):
        if (x, y) == self._position:
            return
        if self._carried is not None:
            return
        item2 = self._model.filter_items(item_kind = self._kind_name,
                                        position = (x,y),
                                        return_first = True)[0]
        if item2 is not None:
            if item2.get_carried() is not None:
                return
            item2.set_position(self._position[0], self._position[1])
            item2.set_starting_position(self._position[0], self._position[1])
        self.set_position(x,y)
        self.set_starting_position(x, y)

    # This is a overridden QT function and used for drag and drop.
    def mousePressEvent(self, event):
        if self._carried is not None:
            self._carried.mousePressEvent(event)
        else:
            super(self.__class__, self).mousePressEvent(event)

    # This is a overridden QT function and used for drag and drop.
    def mouseMoveEvent(self, event):
        if self._carried is not None:
            self._carried.mouseMoveEvent(event)
        else:
            super(self.__class__, self).mouseMoveEvent(event)

    # This is a overridden QT function and used for drag and drop.
    def mouseReleaseEvent(self, event):
        if self._carried is not None:
            self._carried.mouseReleaseEvent(event)
        else:
            super(self.__class__, self).mouseReleaseEvent(event)

class Robot(VisualizerGraphicItem):
    def __init__(self, ID = 0, x = 0, y = 0):
        super(self.__class__, self).__init__(ID, x, y)
        self._kind_name = 'robot'
        self._carries = None
        self._initial_carries = None
        self._tasks = []
        self._graphics_item = QGraphicsRectItem(self)
        self._energy_bar_full = QGraphicsRectItem(self)
        self._energy_bar_empty = QGraphicsRectItem(self)
        self._text = QGraphicsTextItem(self)
        self.setZValue(1.0)

        self._energy_bar_empty.setBrush(QBrush(QColor(200,0,0)))
        self._energy_bar_full.setBrush(QBrush(QColor(0,200,0)))

        self._max_energy = 0
        self._current_energy = 0
        self._energy_costs = {}

    def set_position(self, x, y):
        super(self.__class__, self).set_position(x, y)
        if self._carries is not None:
           self._carries.set_position(x, y)

    def set_starting_position(self, x, y):
        super(self.__class__, self).set_starting_position(x, y)
        if self._initial_carries is not None:
           self._initial_carries.set_starting_position(x, y)

    def set_carries(self, shelf):
        if shelf == self._carries:
            return
        old = self._carries
        self._carries = shelf
        if old != None: old.set_carried(None)
        if self._carries != None: self._carries.set_carried(self)

    def set_initial_carries(self, shelf):
        self._initial_carries = shelf

    def set_rect(self, rect):
        scale = config.get('display', 'id_font_scale')
        bold = config.get('display', 'id_font_bold')
        self._text.setFont(QFont('', rect.width()*0.08*scale))
        self._text.setPos(rect.x(), rect.y() + 0.2*rect.height())
        self._text.setDefaultTextColor(QColor(config.get('display', 'id_font_color')))
        rect2 = QRectF()

        if self._display_mode == 0:
            if bold:
                self._text.setHtml('<b>R(' + str(self._id) + ')</b>')
            else:
                self._text.setHtml('R(' + str(self._id) + ')')
            if not self._highlighted:
                rect2 = QRectF(rect.x() + 0.25*rect.width(), 
                               rect.y() + 0.25*rect.height(),
                               rect.width()*0.5,
                               rect.height()*0.5)
            else:
                rect2 = QRectF(rect.x() + 0.05*rect.width(), 
                               rect.y() + 0.05*rect.height(),
                               rect.width()*0.9,
                               rect.height()*0.9,)

        else:
            self._text.setPlainText('')
            if not self._highlighted:
                rect2 = QRectF(rect.x() + 0.05*rect.width(), 
                               rect.y() + 0.05*rect.height(),
                               rect.width()*0.9,
                               rect.height()*0.9)
            else:
                rect2 = QRectF(rect.x() - 0.15*rect.width(), 
                               rect.y() - 0.15*rect.height(),
                               rect.width()*1.3,
                               rect.height()*1.3,)

        self._graphics_item.setRect(rect2)
        #draw energy bar if max energy > 0
        if self._max_energy > 0:
            per_energy = max(0.0, min(1.0, float(self._current_energy) / self._max_energy))
            rect2.setLeft(rect2.x() + rect2.width()*0.7)
            rect2.setWidth(rect2.width()*0.5)

            self._energy_bar_empty.setRect(rect2.x(), 
                                           rect2.y(),
                                           rect2.width(),
                                           rect2.height() * (1.0 - per_energy))
            self._energy_bar_full.setRect(rect2.x(), 
                                          rect2.y() + rect2.height() * (1.0 - per_energy), 
                                          rect2.width(), 
                                          rect2.height() * per_energy)

        if self._carries is not None:
            self._carries.set_rect(rect)
        self.update_tooltip()

    def set_current_energy(self, energy):
        self._current_energy = energy

    def set_max_energy(self, energy):
        self._max_energy = energy

    def add_energy(self, energy):
        self._current_energy = self._current_energy + energy

    def add_task(self, task):
        if task is None:
            return
        if task in self._tasks:
            return
        self._tasks.append(task)
        task.set_robot(self)

    def parse_init_value(self, name, value):
        result = super(self.__class__, self).parse_init_value(name, value)
        if result <= 0: return result
        if name == 'carries':
            shelf = self._model.get_item('shelf', value, True, True)
            self.set_initial_carries(shelf)
            self.set_carries(shelf)
            return 0
        elif name == 'energy':
            self.set_current_energy(value.number)
            return 0
        elif name == 'max_energy':
            self.set_max_energy(value.number)
            return 0
        elif name == 'energy_cost':
            self._energy_costs[value.arguments[0].name] = value.arguments[1].number
            return 0
        return 1

    def update_tooltip(self):
        tooltip = ("robot(" + str(self._id) + ")\nenergy: " + 
                   str(self._current_energy) + "/" + 
                   str(self._max_energy))
        if self._max_energy > 0:
            tooltip += ("(" + 
                        str(float(self._current_energy)/self._max_energy) + 
                        "%)")
        
        self.setToolTip(tooltip)

    def restart(self):
        super(self.__class__, self).restart()
        self.set_carries(self._initial_carries)

    def to_init_str(self):
        s = super(self.__class__, self).to_init_str()
        if self._initial_carries is not None:
            s += ("init(object(robot,"
                    + str(self._id) + "),value(carries,"
                    + str(self._initial_carries.get_id())
                    + ")).")
        s += ("init(object(robot," 
                + str(self._id) + "), value(max_energy,"
                + str(self._max_energy)
                + ")).")
        s += ("init(object(robot," 
                + str(self._id) + "), value(energy,"
                + str(self._current_energy)
                + ")).")
        for key in self._energy_costs:
            s += ("init(object(robot,"
                    + str(self._id) + "),value(energy_cost, ("
                    + key + ", " + str(self._energy_costs[key]) + "))).")
        return s

    def do_action(self, time_step):
        self._state = self._state & ~VIZ_STATE_ACTION

        #sets the state for the next action
        if time_step + 1 < len(self._actions):
            if self._actions[time_step + 1] is not None:
                action = self._actions[time_step + 1].arguments[0]
                if action.name == 'move':
                    self._state = self._state | VIZ_STATE_MOVE
                elif action.name == 'deliver':
                    self._state = self._state | VIZ_STATE_DELIVER
                elif action.name == 'pickup':
                    self._state = self._state | VIZ_STATE_PICK_UP
                elif action.name == 'putdown':
                    self._state = self._state | VIZ_STATE_PUT_DOWN2
                elif action.name == 'charge':
                    self._state = self._state | VIZ_STATE_CHARGE


        if time_step >= len(self._actions):
            return 0  #break, if no action is defined
        if self._actions[time_step] is None:
            return 0  #break, if no action is defined
        if self._model is None:
            return -3

        try:
            action = self._actions[time_step].arguments[0]
            value = self._actions[time_step].arguments[1]
        except:
            return -1

        #energy cost
        if str(action.name) in self._energy_costs:
            try:
                self.add_energy(-self._energy_costs[action.name])
            except:
                print("Energy cost is not an integer.")
                self._energy_costs[action.name] = None

        #do action
        if action.name == 'move':
            if len(value.arguments) != 2: 
                return -1
            try:
                move_x = value.arguments[0].number
                move_y = value.arguments[1].number
                self.set_position(self._position[0] + move_x, self._position[1] + move_y)
                self._state = self._state | VIZ_STATE_MOVED
            except:
                self.set_position(self._position[0], self._position[1])

            for task in self._tasks:
                for checkpoint in task.get_checkpoints():
                    checkpoint = checkpoint[0]
                    pos = checkpoint.get_position()
                    if pos[0] == self._position[0] and pos[1] == self._position[1]:
                        task.visit_checkpoint(checkpoint)
                        break
            return 1

        elif action.name == 'pickup':
            shelf = self._model.filter_items(item_kind = 'shelf',
                        position = self._position,
                        return_first = True)[0]
            if shelf is None:
                return -2
            self.set_carries(shelf)
            self._state = self._state | VIZ_STATE_PICKED_UP
            return 2

        elif action.name == 'putdown':
            if self._carries == None:
                return -2
            self.set_carries(None)
            self._state = self._state | VIZ_STATE_PUT_DOWN
            return 3

        elif action.name == 'deliver' and len(value.arguments) > 2:
            try:
                if self._carries is not None:
                    self._carries.remove_product(value.arguments[1], value.arguments[2].number)
                order = self._model.filter_items(item_kind = 'order', 
                            ID = value.arguments[0], 
                            return_first = True)[0]
                if order is None:
                    return -2
                order.deliver(value.arguments[1], value.arguments[2].number, time_step)
                self._state = self._state | VIZ_STATE_DELIVERED
            except:
                return -3
            return 4

        elif action.name == 'deliver' and len(value.arguments) > 1:
            try:
                if self._carries is not None:
                    self._carries.remove_product(value.arguments[1], 0)
                order = self._model.filter_items(item_kind = 'order', 
                            ID = value.arguments[0], 
                            return_first = True)[0]
                if order is None:
                    return -2
                order.deliver(value.arguments[1], 0, time_step)
                self._state = self._state | VIZ_STATE_DELIVERED
            except:
                return -3
            return 5

        elif action.name == 'charge':
            try:
                self.add_energy(value.number)
            except:
                return -4
            return 6
        return 0

    def undo_action(self, time_step):
        self._state = self._state & ~VIZ_STATE_ACTION
        if time_step >= len(self._actions):  
            return 0  #break, if no action is defined
        if self._actions[time_step] == None: 
            return 0  #break, if no action is defined
        if self._model is None:
            return -3

        try:
            action = self._actions[time_step].arguments[0]
            value = self._actions[time_step].arguments[1]
        except:
            return -1

        #energy cost
        if action.name in self._energy_costs:
            try:
                self.add_energy(self._energy_costs[action.name])
            except:
                print("Energy cost is not an integer.")
                self._energy_costs[action.name] = None

        if action.name == 'move':
            if len(value.arguments) != 2: 
                return -1

            for task in self._tasks:
                for checkpoint in task.get_checkpoints():
                    checkpoint = checkpoint[0]
                    pos = checkpoint.get_position()
                    if pos[0] == self._position[0] and pos[1] == self._position[1]:
                        task.unvisit_checkpoint(checkpoint)
                        break

            try:
                move_x = value.arguments[0].number
                move_y = value.arguments[1].number
                self.set_position(self._position[0] - move_x, self._position[1] - move_y)
                self._state = self._state | VIZ_STATE_MOVE
            except:
                self.set_position(self._position[0], self._position[1])
            if self._carries is not None: 
                self._carries.set_position(self._position[0], self._position[1])
            return 1

        elif action.name == 'putdown':
            shelf = self._model.filter_items(item_kind = 'shelf',
                        position = self._position,
                        return_first = True)[0]
            if shelf is None:
                return -2
            self.set_carries(shelf)
            self._state = self._state | VIZ_STATE_PUT_DOWN2
            return 3

        elif action.name == 'pickup':
            if self._carries == None:
                return -2
            self.set_carries(None)
            self._state = self._state | VIZ_STATE_PICK_UP
            return 2

        elif action.name == 'deliver' and len(value.arguments) > 2:
            try:
                if self._carries is not None:
                    self._carries.remove_product(value.arguments[1], -value.arguments[2].number)
                order = self._model.filter_items(item_kind = 'order',
                            ID = value.arguments[0],
                            return_first = True)[0]
                if order is None:
                    return -2
                order.deliver(value.arguments[1], -value.arguments[2].number, time_step)
                self._state = self._state | VIZ_STATE_DELIVER
            except:
                return -3
            return 4

        elif action.name == 'deliver' and len(value.arguments) > 1:
            try:
                if self._carries is not None:
                    self._carries.remove_product(value.arguments[1], 0)
                order = self._model.filter_items(item_kind = 'order', 
                            ID = value.arguments[0], 
                            return_first = True)[0]
                if order is None:
                    return -2
                order.deliver(value.arguments[1], 0, time_step)
                self._state = self._state | VIZ_STATE_DELIVER
            except:
                return -3
            return 5

        elif action.name == 'charge':
            try:
                self.add_energy(-value.number)
            except:
                return -4
            return 6
        return 0

    def determine_color(self, number, count, pattern = None):
        color = calculate_color(self._colors[0], self._colors[1], (float)(number)/count)
        self._color = color
        brush = QBrush(color)
        self._graphics_item.setBrush(brush)

    def get_rect(self):
        if self._display_mode == 0:
            rect = self._graphics_item.rect()
            width = rect.width()*2
            height = rect.height()*2
            rect.setLeft(rect.x() - 0.25*width)
            rect.setTop(rect.y() - 0.25*height)
            rect.setWidth(width)
            rect.setHeight(height)
            return rect
        elif self._display_mode == 1:
            rect = self._graphics_item.rect()
            width = rect.width()/0.9
            height = rect.height()/0.9
            rect.setLeft(rect.x() - 0.05*width)
            rect.setTop(rect.y() - 0.05*height)
            rect.setWidth(width)
            rect.setHeight(height)
            return rect

    def get_carries(self):
        return self._carries

    def get_initial_carries(self):
        return self._initial_carries

    def can_move(self):
        return True

    def edit_position_to(self, x, y):
        if (x, y) == self._position:
            return
        item2 = self._model.filter_items(item_kind = self._kind_name,
                                        position = (x,y),
                                        return_first = True)[0]
        shelf = self._model.filter_items('shelf',
                                        position = self._position,
                                        return_first = True)[0]
        shelf2 = self._model.filter_items('shelf',
                                        position = (x,y),
                                        return_first = True)[0]

        if shelf2 is not None and shelf is not None:
            if shelf.get_carried() is not None or shelf2.get_carried() is not None:
                shelf.set_position(x,y)
                shelf.set_starting_position(x,y)
                shelf2.set_position(self._position[0], self._position[1])
                shelf2.set_starting_position(self._position, self._position[1])
        if item2 is not None:
            item2.set_position(self._position[0], self._position[1])
            item2.set_starting_position(self._position[0], self._position[1])
        self.set_position(x,y)
        self.set_starting_position(x, y)

    def get_current_energy(self):
        return self._current_energy

    def get_max_energy(self):
        return self._max_energy

class Checkpoint(VisualizerGraphicItem):
    def __init__(self, ID = 0, x = 0, y = 0):
        super(self.__class__, self).__init__(ID, x, y)
        self._kind_name = 'checkpoint'

        self._ids = {}

        self._graphics_item = QGraphicsRectItem(self)
        self._text = QGraphicsTextItem(self._graphics_item)
        self._shine = False

    def set_rect(self, rect):
        scale = config.get('display', 'id_font_scale')
        bold = config.get('display', 'id_font_bold')
        font = QFont('', rect.width()*0.08*scale)
        self._text.setFont(font)
        self._text.setPos(rect.x(), rect.y() + 0.6*rect.height())
        self._text.setDefaultTextColor(QColor(config.get('display', 'id_font_color')))

        if self._display_mode == 0:            
            ss = ''
            if bold:
                ss = '<b>'
            for key in self._ids:
                count = 0
                for ii in self._ids[key]:
                    if count == 0:
                        ss = ss + '(' + key + ': ' + ii[0]
                    else:
                        ss = ss + ', ' + ii[0]
                    count += 1
                ss = ss + ')\n'

            if bold:
                ss += '</b>'

            self._text.setHtml(ss)
            self._graphics_item.setRect(rect.x(), rect.y(), rect.width(), rect.height())

        elif self._display_mode == 1:
            self._text.setPlainText('')
            self._graphics_item.setRect(rect.x(), rect.y(), rect.width(), rect.height())        

    def do_action(self, time_step):
        self._shine = False
        return

    def undo_action(self, time_step):
        self._shine = False
        return

    def visit(self):
        self._shine = True

    def determine_color(self, number, count, pattern = None):
        color = None
        if len(self._ids) == 1:
            for key in self._ids:
                color_id = self._ids[key][0][1] + 1
                if color_id < len(self._colors):
                    color = self._colors[color_id]    
                        
        if color is None:
            color = self._colors[0]

        if self._shine:
            color = calculate_color(color, QColor(255,255,255), 0.4)
        self._graphics_item.setBrush(QBrush(color))

    def parse_init_value(self, name, value):
        result = super(self.__class__, self).parse_init_value(name, value)
        if result != 1:
            return result

        if name == 'checkpoint' and len(value.arguments) == 3:
            if str(value.arguments[0]) not in self._ids:
                self._ids[str(value.arguments[0])] = []
            self._ids[str(value.arguments[0])].append((str(value.arguments[1]), value.arguments[2].number))
            return 0
        return 1

    def get_rect(self):
        return self._graphics_item.rect()
