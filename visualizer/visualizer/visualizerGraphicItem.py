from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QBrush
import modelView 
import visualizerItem
from configuration import *

def calculate_color(first_color, second_color, multiplier):
    red = (min(first_color.red(), second_color.red()), max(first_color.red(), second_color.red()))
    green = (min(first_color.green(), second_color.green()), max(first_color.green(), second_color.green()))
    blue = (min(first_color.blue(), second_color.blue()), max(first_color.blue(), second_color.blue()))
    return QColor(
                red[0] + (red[1] - red[0]) * multiplier,
                green[0] + (green[1] - green[0]) * multiplier,
                blue[0] + (blue[1] - blue[0]) * multiplier)

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
        self._graphics_item = None
        self._text = None
        self._actions = []
        self._colors = [QColor(0,0,0)]
        self._display_mode = 0
        self.setAcceptedMouseButtons(Qt.MouseButtons(1))

    def set_starting_position(self, x, y):
        self._start_position = (x, y)

    def set_position(self, x, y):
        self._position = (x, y)

    def set_color(self, color, color_id = 0):
        while color_id >= len(self._colors):
            self._colors.append(QColor(0,0,0))
        self._colors[color_id] = color

    def set_rect(self, rect):
        return

    def set_action(self, action, time_step):
        if time_step < 0:
            print ('Warning: invalid time step in occurs(object('
                    + str(self._kind_name) + ','
                    + str(self._ID) + '),' + str(action)
                    + ',' + str(time_step) + ')')
            print 'time step is less than 0'
            return
        for ii in range((time_step + 1) - len(self._actions)):
            self._actions.append(None)
        if not self._actions[time_step] == None:
            print ('Warning: for object(' + str(self._kind_name)
                    + ', ' + str(self._id)
                    + ') multiple actions are defined at time step '
                    + str(time_step))
        self._actions[time_step] = action

    def set_display_mode(self, display_mode):
        self._display_mode =  display_mode

    def parse_init_value(self, name, value):
        if value is None or name is None:
            return -1
        if name == 'at':
            pos = (value.arguments[0].number, value.arguments[1].number)
            self.set_starting_position(pos[0], pos[1])
            self.set_position(pos[0], pos[1])
            return 0
        return 1

    def enable_drag(self, enable):
        self._enable_drag = enable

    def restart(self):
        self._position = self._start_position

    def do_action(self, time_step):
        return

    def undo_action(self, time_step):
        return

    def clear_actions(self):
        self._actions = []

    def to_init_str(self):
        return ('init(object('
                + self._kind_name + ','
                + str(self._id) + '), value(at,('
                + str(self._position[0]) + ','
                + str(self._position[1]) + '))).')

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

    def determine_color(self, number, count, pattern = None):
        return

    def get_name(self):
        return self._kind_name

    def get_position(self):
        return self._position

    def get_color(self, color_id):
        if color_id < len(self._colors):
            return self._colors[color_id]
        return None

    def get_rect(self):
        return None

    def get_action(self, time_step):
        if time_step >= len(self._actions):
            return None  #break, if no action is defined
        if self._actions[time_step] == None:
            return None  #break, if no action is defined     
        return self._actions[time_step]   

    def edit_position_to(self, x, y):
        if (x, y) == self._position:
            return
        item2 = self._model.filter_items(item_kind = self._kind_name,
                                        position = (x,y),
                                        return_first = True)[0]
        if item2 is not None:
            item2.set_position(self._position[0], self._position[1])
            item2.set_starting_position(self._position[0], self._position[1])
        self.set_position(x,y)
        self.set_starting_position(x, y)

    def boundingRect(self):
        return self._graphics_item.boundingRect()

    def paint(self, painter, option, widget):
        return self._graphics_item.paint(painter, option, widget)

    def mousePressEvent(self, event):
        if self._enable_drag:
            rect = self.get_rect()
            self._dragged = (event.scenePos().x(),
                             event.scenePos().y())
        event.accept()

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

    def mouseMoveEvent(self, event):
        if self._dragged is None:
            return
        self.setPos(event.scenePos().x() - self._dragged[0], event.scenePos().y() - self._dragged[1])
        event.accept()

class PickingStation(VisualizerGraphicItem):
    def __init__(self, ID = 0, x = 0, y = 0):
        super(self.__class__, self).__init__(ID, x, y)
        self._kind_name = 'pickingStation'

        self._items = []
        self._graphics_item = QGraphicsRectItem(self)
        self._items.append(QGraphicsRectItem(self._graphics_item))
        self._items.append(QGraphicsRectItem(self._graphics_item))
        self._text = QGraphicsTextItem(self._graphics_item)

    def set_rect(self, rect):
        scale = config.get('display', 'id_font_scale')
        bold = config.get('display', 'id_font_bold')
        self._text.setFont(QFont('', rect.width()*0.08*scale))
        self._text.setPos(rect.x(), rect.y() + 0.6*rect.height())
        self._text.setDefaultTextColor(QColor(config.get('display', 'id_font_color')))
        if self._display_mode == 0:
            if bold:
                self._text.setHtml('<b>P(' + str(self._id) + ')</b>')
            else:
                self._text.setHtml('P(' + str(self._id) + ')')
            self._graphics_item.setRect(rect.x(), rect.y(), rect.width(), rect.height())
            self._items[0].setRect(rect.x() + rect.width()/5, rect.y(), rect.width()/5, rect.height())
            self._items[1].setRect(rect.x() + rect.width()/5 * 3, rect.y(), rect.width()/5, rect.height())
        elif self._display_mode == 1:
            self._text.setPlainText('')
            self._graphics_item.setRect(rect.x(), rect.y(), rect.width(), rect.height())
            self._items[0].setRect(rect.x() + rect.width()/5, rect.y(), rect.width()/5, rect.height())
            self._items[1].setRect(rect.x() + rect.width()/5 * 3, rect.y(), rect.width()/5, rect.height())            

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

    def get_rect(self):
        return self._graphics_item.rect()

class Shelf(VisualizerGraphicItem):
    def __init__(self, ID = 0, x = 0, y = 0):
        super(self.__class__, self).__init__(ID, x, y)
        self._kind_name = 'shelf'
        self._carried = None
        self._products   = []
        self._graphics_item = QGraphicsEllipseItem(self)
        self._graphics_carried = QGraphicsEllipseItem()
        self._text = QGraphicsTextItem(self)
        self.setZValue(2.0)
        self.update_tooltip()

    def set_rect(self, rect):
        if self._carried is not None:
            rect = self._carried.get_rect()

        scale = config.get('display', 'id_font_scale')
        bold = config.get('display', 'id_font_bold')
        self._text.setFont(QFont('', rect.width()*0.08*scale))
        self._text.setPos(rect.x(), rect.y() + 0.4*rect.height())
        self._text.setDefaultTextColor(QColor(config.get('display', 'id_font_color')))

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

    def set_carried(self, robot):
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

    def restart(self):
        super(self.__class__, self).restart()
        products = []
        for product in self._products:
            products.append((product[0], product[1], 0))
        self._products = products

    def to_init_str(self):
        s = super(self.__class__, self).to_init_str()
        for product in self._products:
            s += ('\ninit(object(product,' 
                    + str(product[0]) + '),value(on,('
                    + str(self._id) + ',' 
                    + str(product[1]) + '))).')
        return s

    def update_tooltip(self):
        tooltip = "shelf(" + str(self._id) + ")\nproducts:\n"
        for product in self._products:
            tooltip = tooltip + str(product) + "\n"
        self.setToolTip(tooltip)

    def find_product(self, product_id):
        for product in self._products:
            if str(product_id) == str(product[0]):
                return product
        return None

    def set_product_amount(self, product_id, amount):
        product = self.find_product(product_id)
        if product is None:
            self._products.append((product_id, amount, 0))
        else:
            self._products.remove(product)
            self._products.append((product_id, amount, product[2]))
        self.update_tooltip()

    def add_product(self, product_id, amount):
        product = self.find_product(product_id)
        if product is None:
            if amount == 0:
                amount = 1
            self._products.append((product_id, amount, 0))
        else: 
            if amount == 0:
                self._products.append((product_id, 0, 0))
            else:
                self._products.append((product_id, product[1] + amount, 0))
            self._products.remove(product)
        self.update_tooltip()

    def remove_product(self, product_id, amount):
        product = self.find_product(product_id)
        if product is not None:
            self._products.append((product_id, product[1], product[2] + amount))
            self._products.remove(product)

    def delete_product(self, product_id):
        product = self.find_product(product_id)
        if product is not None:
            self._products.remove(product)
        self.update_tooltip()

    def determine_color(self, number, count, pattern = None):
        color = calculate_color(self._colors[0], self._colors[1], (float)(number)/count)
        brush = QBrush(color)
        self._graphics_item.setBrush(brush)
        self._graphics_carried.setBrush(QBrush(self._colors[2]))

    def get_product_amount(self, product_id):
        product = self.find_product(product_id)
        if product is None:
            return 0
        return product[1] - product[2]

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

    def get_carried(self):
        return self._carried

    def iterate_products(self):
        for product in self._products:
            yield product

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

    def mousePressEvent(self, event):
        if self._carried is not None:
            self._carried.mousePressEvent(event)
        else:
            super(self.__class__, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._carried is not None:
            self._carried.mouseMoveEvent(event)
        else:
            super(self.__class__, self).mouseMoveEvent(event)

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
        self._text = QGraphicsTextItem(self)
        self.setZValue(1.0)

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

        if self._display_mode == 0:
            if bold:
                self._text.setHtml('<b>R(' + str(self._id) + ')</b>')
            else:
                self._text.setHtml('R(' + str(self._id) + ')')
            self._graphics_item.setRect(rect.x() + 0.25*rect.width(), 
                                        rect.y() + 0.25*rect.height(),
                                        rect.width()*0.5,
                                        rect.height()*0.5,)

        elif self._display_mode == 1:
            self._text.setPlainText('')
            self._graphics_item.setRect(rect.x() + 0.05*rect.width(),
                                        rect.y() + 0.05*rect.height(),
                                        rect.width()*0.9,
                                        rect.height()*0.9)

        if self._carries is not None:
            self._carries.set_rect(rect)

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
        return 1

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
        return s

    def do_action(self, time_step):
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

        if action.name == 'move':
            if len(value.arguments) != 2: 
                return -1
            try:
                move_x = value.arguments[0].number
                move_y = value.arguments[1].number
                self.set_position(self._position[0] + move_x, self._position[1] + move_y)
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
            return 2

        elif action.name == 'putdown':
            if self._carries == None:
                return -2
            self.set_carries(None)
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
            except:
                return -3
            return 5
        return 0

    def undo_action(self, time_step):
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
            return 3

        elif action.name == 'pickup':
            if self._carries == None:
                return -2
            self.set_carries(None)
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
            except:
                return -3
            return 5
        return 0

    def determine_color(self, number, count, pattern = None):
        color = calculate_color(self._colors[0], self._colors[1], (float)(number)/count)
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
