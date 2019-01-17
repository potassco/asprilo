from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from .configuration import *
from .model import *
    
class MainScene(QGraphicsScene):
    def __init__(self):
        super(self.__class__, self).__init__()

class ModelView(QGraphicsView):
    def __init__(self):
        super(self.__class__, self).__init__()
        self._scene = MainScene()
        self.setScene(self._scene)
 
        self._model = None

        self._object_size = 35
        self._screen_width  = 600
        self._screen_height = 600
        self._border_size = 3             #the size of the borders of the grid

        self._h_distance = 60             #the size of one grid cell
        self._w_distance = 60

        self._line_hlength = self._w_distance
        self._line_vlength = self._h_distance

        self._display_mode = 0
        self._scaling = 1.0
        self._zoom = (1.0, 1.0)

        self._grid_size_x = 1
        self._grid_size_Y = 1
        self._lines = []

        self._items_in_scene = []

        self._timer = None
        self._timer_count = 1
        self._timer_scale = 1.0

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.resize(self._screen_width, self._screen_height)
        self._menu = QMenu()
        self._menu.setParent(self)
        self.setToolTip('tooltip')

    def contextMenuEvent(self, event):
        if self._model == None:
            return

        point = self.mapToScene(event.x(), event.y())
        node = self.scene_coordinates_to_grid(point.x(), point.y())
        if node is None:
            return
        x = node[0]
        y = node[1]

        if not self._model.get_editable():
            return 

        self._menu.clear()

        if self._model.is_node(x,y):
            action = QAction('disable node', self)
            action.setShortcut('Ctrl + N')
            action.setStatusTip('Disables the selected node')
            action.triggered.connect(lambda: self._remove_node(x, y))
            self._menu.addAction(action)   
        else:
            action = QAction('enable node', self)
            action.setShortcut('Ctrl + N')
            action.setStatusTip('Enables the selected node')
            action.triggered.connect(lambda: self._add_node(x, y))
            self._menu.addAction(action) 

        if self._model.is_highway(x,y):
            action = QAction('remove highway', self)
            action.setShortcut('Ctrl + H')
            action.setStatusTip('Removes a highway from the selected node')
            action.triggered.connect(lambda: self._remove_highway(x,y))
            self._menu.addAction(action)                 
        elif self._model.is_node(x,y):
            action = QAction('add highway', self)
            action.setShortcut('Ctrl + H')
            action.setStatusTip('Adds a highway to the selected node')
            action.triggered.connect(lambda: self._add_highway(x,y))
            self._menu.addAction(action)                   

        robot = self._model.filter_items('robot', position = (x,y), return_first = True)[0]
        shelf = self._model.filter_items('shelf', position = (x,y), return_first = True)[0]

        if robot is not None:
            if shelf is not None: 
                if robot.get_initial_carries() is not None:
                    action = QAction('putdown', self)
                    action.setShortcut('Ctrl + P')
                    action.setStatusTip('The robot in the selected node puts down the carried shelf')
                    action.triggered.connect(lambda: self._pickup(robot, None))
                    self._menu.addAction(action)
                else:
                    action = QAction('pickup', self)
                    action.setShortcut('Ctrl + P')
                    action.setStatusTip('The robot in the selected node picks up the shelf in the selcted node')
                    action.triggered.connect(lambda: self._pickup(robot, shelf))
                    self._menu.addAction(action)

                    action = QAction('remove robot', self)
                    action.setShortcut('Ctrl + R')
                    action.setStatusTip('Removes a robot from the selected node')
                    action.triggered.connect(lambda: self._remove_item(robot))
                    self._menu.addAction(action)
            else:
                action = QAction('remove robot', self)
                action.setShortcut('Ctrl + R')
                action.setStatusTip('Removes a robot from the selected node')
                action.triggered.connect(lambda: self._remove_item(robot))
                self._menu.addAction(action)

        elif self._model.is_node(x,y):
            action = QAction('add robot', self)
            action.setShortcut('Ctrl + R')
            action.setStatusTip('Adds a robot to the selected node')
            action.triggered.connect(lambda: self._add_item('robot', x, y))
            self._menu.addAction(action)

        if shelf is not None:
            action = QAction('remove shelf', self)
            action.setShortcut('Ctrl + S')
            action.setStatusTip('Removes a shelf from the selected node')
            action.triggered.connect(lambda: self._remove_item(shelf))
            self._menu.addAction(action)
        elif self._model.is_node(x,y):
            action = QAction('add shelf', self)
            action.setShortcut('Ctrl + S')
            action.setStatusTip('Adds a shelf to the selected node')
            action.triggered.connect(lambda: self._add_item('shelf', x, y))
            self._menu.addAction(action)

        station = self._model.filter_items('pickingStation', position = (x,y), return_first = True)[0]
        if station is not None:
            action = QAction('remove picking station', self)
            action.setShortcut('Ctrl + I')
            action.setStatusTip('Removes a picking station from the selected node')
            action.triggered.connect(lambda: self._remove_item(station))
            self._menu.addAction(action)
        elif self._model.is_node(x,y):
            action = QAction('add picking station', self)
            action.setShortcut('Ctrl + I')
            action.setStatusTip('Adds a picking Station to the selected node')
            action.triggered.connect(lambda: self._add_item('pickingStation', x, y))
            self._menu.addAction(action)           

        station2 = self._model.filter_items('chargingStation', position = (x,y), return_first = True)[0]
        if station is not None:
            action = QAction('remove charging station', self)
            action.setShortcut('Ctrl + B')
            action.setStatusTip('Removes a charging station from the selected node')
            action.triggered.connect(lambda: self._remove_item(station))
            self._menu.addAction(action)
        elif self._model.is_node(x,y):
            action = QAction('add charging station', self)
            action.setShortcut('Ctrl + B')
            action.setStatusTip('Adds a charging Station to the selected node')
            action.triggered.connect(lambda: self._add_item('chargingStation', x, y))
            self._menu.addAction(action)

        self._menu.popup(QPoint(event.x(),event.y()))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton or event.button() == Qt.MiddleButton:
            self._menu.hide()
        super(self.__class__, self).mousePressEvent(event)

    def event(self, event):
        if event.type() == QEvent.ToolTip:
            pos = self.mapToScene(event.pos())
            pos = self.scene_coordinates_to_node(pos.x(), pos.y())
            if pos is None:
                self.setToolTip('')
                return super(self.__class__, self).event(event)
            ss = 'node(' + str(self._model.get_node_id(pos)) +') at ' + str(pos)
            for item in self._model.filter_items(position = pos):
                ss += '\n' + item.get_name() + '('+ str(item.get_id()) +')'
            self.setToolTip(ss)
        return super(self.__class__, self).event(event)

    def _pickup(self, robot, shelf):
        robot.set_initial_carries(shelf)
        robot.set_carries(shelf)
        self._menu.hide()
        self._model.update_windows()

    def _add_highway(self, x, y):
        self._model.add_highway(x, y)
        self._menu.hide()
        self._model.update_windows()
    
    def _remove_highway(self, x, y):
        self._model.remove_highway(x, y)
        self._menu.hide()
        self._model.update_windows()

    def _add_node(self, x, y):
        self._model.add_node(x, y)
        self._menu.hide()
        self._model.update_windows()
    
    def _remove_node(self, x, y):
        self._model.remove_node(x, y)
        self._menu.hide()
        self._model.update_windows()

    def _add_item(self, kind, x, y):
        item = self._model.create_item(kind, add_immediately = True)
        item.set_starting_position(x, y)
        item.set_position(x, y)
        self._menu.hide()
        self._model.update_windows()
    
    def _remove_item(self, item):
        self._model.remove_item(item)
        self._menu.hide()
        self._model.update_windows()

    def set_model(self, model):
        if self._model is not None:
            self._model.remove_window(self)
        self._model = model
        if self._model is not None:
            self._model.add_window(self)
        self.resize_to_fit()
        self.update()

    def start_timer(self):
        self.stop_timer()
        self._timer = QTimer()
        self._timer.timeout.connect(lambda: self.update_model(False))
        self.adjust_timer()

    def adjust_timer(self):
        timeout = (config.get('visualizer', 'step_time') / 10) * self._timer_scale
        if timeout < 10:
            timeout = 10
        if self._timer is not None:
            self._timer.start(timeout)

    def switch_timer(self):
        if self._timer is None:
            self.start_timer()
        else:
            self.stop_timer()

    def stop_timer(self):
        if self._timer is not None:
            self._timer.stop()
            self._timer_count = 0
            self._timer = None

    def speed_up_timer(self, speed_up):
        self._timer_scale *= 1 - speed_up
        if self._timer_scale <= 0.1:
            self._timer_scale = 0.1
        self.adjust_timer()

    def get_timer_speedup(self):
        return self._timer_scale

    def is_timer_running(self):
        return self._timer is None

    def update_model(self, forced):
        if self._model == None: 
            return
        if self._timer_count >= 10 or forced:
            self._model.update()
            self._timer_count = 0
        else: 
            self._timer_count += 1
        self.update()

    def undo_model(self):
        if self._model is None: 
            return
        self._model.undo()
        self.update()

    def _scale(self, scale_x, scale_y):
        old_zoom = min(self._zoom[0], self._zoom[1])
        new_zoom = min(self._zoom[0]*scale_x, self._zoom[1]*scale_y)
        scale = new_zoom/old_zoom
        if old_zoom < 1.0:
            scale = new_zoom
        if  new_zoom >= 1.0:
            self.scale(scale, scale)
            self._display_mode = 0
            self._scaling = 1.0
            self._border_size = 3
        else:
            if self._display_mode == 0:
                self.scale(1.0/old_zoom, 1.0/old_zoom)
            self._display_mode = 1
            self._scaling = min(self._zoom[0]*scale_x, self._zoom[1]*scale_y)
            self._border_size = 2
            if new_zoom < 0.5:
                self._border_size = 1                
        self._zoom = (self._zoom[0]*scale_x, self._zoom[1]*scale_y)
        self.update()

    def wheelEvent(self, event):
        self.zoom_event(event.angleDelta().y())

    def zoom_event(self, angle):
        zoom = (1.0 + angle/1440.0)
        self._scale(zoom, zoom)

    def resizeEvent(self, event):
        super(self.__class__, self).resizeEvent(event)
        if (event.oldSize().width() < 1 
            or event.oldSize().height() < 1 
            or event.size().width() < 1 
            or event.size().height() < 1):
            return
        self._screen_width  = event.size().width()
        self._screen_height = event.size().height()
        scaling = ((float)(self._screen_width) / (event.oldSize().width()), 
                    (float)(self._screen_height) / (event.oldSize().height()))
        self._scale(scaling[0], scaling[1])

    def resize_to_fit(self):
        if self.width() <= 1 or self.height() <= 1: 
            return
        zoom = ((float)(self._screen_width) / (self._line_hlength*1.04), 
                (float)(self._screen_height) / (self._line_vlength*1.04))

        self._scale(zoom[0]/self._zoom[0], zoom[1]/self._zoom[1])
        self._scene.setSceneRect(0, 0, self._line_hlength, self._line_vlength*1)

    def clear(self):
        for line in self._lines:
            self._scene.removeItem(line)
        self._lines = []

        for item in self._items_in_scene:
            self._scene.removeItem(item)
        self._items_in_scene = []

    def update(self):
        if self._model == None: 
            return 0
        self._line_hlength = (self._w_distance) * self._model.get_grid_size()[0] + self._border_size
        self._line_vlength = (self._h_distance) * self._model.get_grid_size()[1] + self._border_size

        for item_dic in self._model.iterate_graphic_dictionaries():
            for item in item_dic.values():
                color_id = 0
                hex_color = config.get('color', 'color_' + item.get_kind_name() + str(color_id))
                while(hex_color is not None):
                    item.set_color(QColor(hex_color), color_id)
                    color_id += 1
                    hex_color = config.get('color', 'color_' + item.get_kind_name() + str(color_id))

        pen = QPen()
        pen.setWidth(self._border_size)
        brush_disabled_node = QBrush(QColor(config.get('color', 'color_disabled_node')))
        brush_highway = QBrush(QColor(config.get('color', 'color_highway')))

        self.clear()

        #draw vertival lines
        for i in range(0,self._model.get_grid_size()[1] + 1):
            line = self._scene.addLine(0, i * self._h_distance*self._scaling,
                                        self._line_hlength*self._scaling - self._border_size,
                                        i *(self._h_distance*self._scaling), pen)
            self._lines.append(line)

        #draw horizontal lines
        for i in range(0,self._model.get_grid_size()[0] + 1):
            line = self._scene.addLine(i * self._w_distance*self._scaling, 
                                        0, i * (self._w_distance*self._scaling), 
                                        self._line_vlength*self._scaling - self._border_size, pen)
            self._lines.append(line)

        #draw disabled nodes
        for node in self._model.get_blocked_nodes():
            xPos = (node[0]-1) * self._w_distance
            yPos = (node[1]-1) * self._h_distance
            rect = self._scene.addRect(xPos*self._scaling, 
                                        yPos*self._scaling, 
                                        self._w_distance*self._scaling, 
                                        self._h_distance*self._scaling, 
                                        pen, brush_disabled_node)
            self._items_in_scene.append(rect)

        #draw highways
        for node in self._model.get_highways():
            xPos = (node[0]-1) * self._w_distance
            yPos = (node[1]-1) * self._h_distance
            rect = self._scene.addRect(xPos*self._scaling, 
                                        yPos*self._scaling, 
                                        self._w_distance*self._scaling, 
                                        self._h_distance*self._scaling, 
                                        pen, brush_highway)
            self._items_in_scene.append(rect)

        #draw items
        for item_dic in self._model.iterate_graphic_dictionaries():
            count = len(item_dic)
            number = 1
            for item in item_dic.values():
                item.set_display_mode(self._display_mode)
                x_pos = item.get_position()[0] - 1
                y_pos = item.get_position()[1] - 1
                action = item.get_action(self._model.get_current_step())
                if action is not None:
                    action_name = action.arguments[0].name
                    action_value = action.arguments[1]
                    if action_name == 'move':
                        action_x = action_value.arguments[0].number
                        action_y = action_value.arguments[1].number
                        x_pos = float(x_pos + float(action_x * float(self._timer_count * 0.1)))
                        y_pos = float(y_pos + float(action_y * float(self._timer_count * 0.1)))
                x_pos = x_pos*self._w_distance*self._scaling + self._border_size/2
                y_pos = y_pos*self._h_distance*self._scaling + self._border_size/2
                item.set_rect(QRect(x_pos, y_pos,
                                self._w_distance*self._scaling - self._border_size*self._scaling,
                                self._h_distance*self._scaling - self._border_size*self._scaling))
                item.determine_color(number, count)

                #draw path
                if item.get_draw_path():
                    x_pos = item.get_position()[0]
                    y_pos = item.get_position()[1]
                    pen = QPen(item.get_color())
                    pen.setWidth(self._border_size)
                    if number % 4 == 0:
                        pen.setStyle(Qt.DashLine)
                    elif number % 3 == 0:
                        pen.setStyle(Qt.DashDotLine)
                    elif number % 2 == 0:
                        pen.setStyle(Qt.DashDotLine)                    
                    cc = self._model.get_current_step()
                    while(cc <= self._model.get_num_steps()):
                        action = item.get_action(cc)
                        cc = cc + 1
                        if action is not None:
                            if action.arguments[0].name == 'move':
                                action_value = action.arguments[1]

                                x_posf = (x_pos-0.5)*self._w_distance*self._scaling
                                y_posf = (y_pos-0.5)*self._h_distance*self._scaling
                                x2_posf = (x_pos+action_value.arguments[0].number-0.5)*self._w_distance*self._scaling
                                y2_posf = (y_pos+action_value.arguments[1].number-0.5)*self._h_distance*self._scaling
                                x_pos = x_pos + action_value.arguments[0].number
                                y_pos = y_pos + action_value.arguments[1].number
                                line = self._scene.addLine(x_posf, y_posf, x2_posf, y2_posf, pen)
                                self._items_in_scene.append(line)

                self._scene.addItem(item)
                self._items_in_scene.append(item)
                number += 1

    def scene_coordinates_to_grid(self, x, y):
        if (x < 0 or y < 0 
            or x > self._line_hlength*self._scaling 
            or y > self._line_vlength*self._scaling):
            return None
        result = (int(x/(self._w_distance*self._scaling) + 1),
                    int(y/(self._h_distance*self._scaling) + 1))
        if result[0] > self._model.get_grid_size()[0]:
            result = (self._model.get_grid_size()[0], result[1])
        if result[1] > self._model.get_grid_size()[1]:
            result = (result[0], self._model.get_grid_size()[1])
        return result

    def scene_coordinates_to_node(self, x, y):
        node = self.scene_coordinates_to_grid(x,y)
        if node is None:
            return None
        if self._model.is_node(node[0], node[1]):
            return node
        return None

    def get_model(self):
        return self._model
