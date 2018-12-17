from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from . import configuration
import os
import sys

VIZ_STATE_MOVED     = 0x01
VIZ_STATE_DELIVERED = 0x02
VIZ_STATE_PICKED_UP = 0x04
VIZ_STATE_PUT_DOWN  = 0x08
VIZ_STATE_MOVE      = 0x10
VIZ_STATE_DELIVER   = 0x20
VIZ_STATE_PICK_UP   = 0x40
VIZ_STATE_PUT_DOWN2 = 0x80
VIZ_STATE_ACTION    = 0xff

class VizWidget(QWidget):
    def __init__(self):
        super(VizWidget, self).__init__()

    def release_widget(self):
        parent = self.parent()
        if parent is not None:
            self.setParent(None)
            self.show()

    def mousePressEvent(self, event):
        QWidget.mousePressEvent(self, event)
        if(event.isAccepted()):
            return
        #if(event.button() is not Qt.LeftButton):
        #    return
        event.accept()
        self.release_widget()
        self.move(event.globalX(), event.globalY())
        self.grabMouse()

    def mouseMoveEvent(self, event):
        self.move(event.globalX(), event.globalY())

    def mouseReleaseEvent(self, event):
        self.releaseMouse()
        widget_manager.drop_widget(self, event.globalX(), event.globalY())

class VizSplitter(QSplitter):
    def __init__(self):
        super(VizSplitter, self).__init__()
        self._childrean_count = 0

    def add_widget(self, widget):
        splitter.addWidget(widget)
        widget.show()
  
    def closeEvent(self, close):
        for ii in range (0, self.count()):
            widget = self.widget(ii)
            if widget.parent() is self:
                widget.setParent(None)
                widget.hide()
        widget_manager.remove(self)

    def childEvent(self, event):
        if event.added() is True:
            self._childrean_count += 1
        elif event.removed() is True:
            self._childrean_count -= 1
        else:
            return
        if self._childrean_count <= 1 and event.removed() is True:
            self.close()

class VizModelWidget(VizWidget):
    def __init__(self):
        super(VizModelWidget, self).__init__()
        self._model = None
 
    def update_model(self):
        pass

    def update_step(self):
        pass

    def set_model(self, model):
        self._model = model
        if self._model is not None:
            self._update_model

class WidgetManager(object):
    def __init__(self):
        self._splitter = []
        self._main_widget = None

    def add(self, widget):
        self._splitter.append(widget)

    def set_main_widget(self, widget):
        self._main_widget = widget

    def remove(self, widget):
        for splitter in self._splitter:
            if widget is splitter:
                self._splitter.remove(splitter)
                return

    def exit(self):
        for splitter in self._splitter:
            splitter.close()

    def drop_widget(self, widget, x, y):
        if widget is None:
            return
        #main widget
        if self._main_widget is not None:
            splitter = self._main_widget.get_splitter()
            splitter_pos = splitter.mapToGlobal(splitter.pos())
            if (splitter_pos.x() < x and splitter_pos.y() < y and
                splitter_pos.x() + splitter.size().width() > x and
                splitter_pos.y() + splitter.size().height() > y):
                pos = splitter_pos.x()
                index = 0
                for size in splitter.sizes():
                    if x > pos and x < pos + size:
                        if x < pos + size/2:
                            splitter.insertWidget(index, widget)
                            splitter.resize(splitter.width() + widget.width(), splitter.height())
                            return
                        else:
                            splitter.insertWidget(index + 1, widget)
                            splitter.resize(splitter.width() + widget.width(), splitter.height())
                            return
                    else:
                        pos += size
                        index += 1

        #other widgets
        for splitter in self._splitter:
            if (splitter.pos().x() < x and splitter.pos().y() < y and
                splitter.pos().x() + splitter.size().width() > x and
                splitter.pos().y() + splitter.size().height() > y):
                pos = splitter.pos().x()
                index = 0
                for size in splitter.sizes():
                    if x > pos and x < pos + size:
                        if x < pos + size/2:
                            splitter.insertWidget(index, widget)
                            splitter.resize(splitter.width() + widget.width(), splitter.height())
                            return
                        else:
                            splitter.insertWidget(index + 1, widget)
                            splitter.resize(splitter.width() + widget.width(), splitter.height())
                            return
                    else:
                        pos += size
                        index += 1

        #create new widget
        splitter = VizSplitter()
        splitter.insertWidget(0, widget)
        splitter.resize(widget.size())
        splitter.move(x,y)
        widget.show()
        splitter.show()
        self._splitter.append(splitter)

widget_manager = WidgetManager()

class InstanceFileTree(QTreeView):
    def __init__(self, widget):
        super(InstanceFileTree, self).__init__(widget)
        self._menu = QMenu()
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self._parser = None

    def contextMenuEvent(self, event):
        self._menu.clear()

        action = QAction('load instance', self)
        action.setStatusTip('Load the selected instance. Delete the current model.')
        action.triggered.connect(lambda: self._load_selected(clear = True, clear_actions = False, ground = True))
        self._menu.addAction(action)

        action = QAction('load plan', self)
        action.setStatusTip('Load the selected plan. Delete actions but keeps the model.')
        action.triggered.connect(lambda: self._load_selected(clear = False, clear_actions = True, ground = True))
        self._menu.addAction(action)

        action = QAction('parse file', self)
        action.setStatusTip('Load the selected file and adds all atoms to the current model.')
        action.triggered.connect(lambda: self._load_selected(clear = False, clear_actions = False, ground = True))
        self._menu.addAction(action)

        action = QAction('load file', self)
        action.setStatusTip('Load the selected file and add it to the parser. Adds nothing to the current model.')
        action.triggered.connect(lambda: self._load_selected(clear = False, clear_actions = False, ground = False))
        self._menu.addAction(action)

        self._menu.popup(self.mapToGlobal(QPoint(event.x(),event.y())))

    def _load_selected(self, clear = True, clear_actions = False, ground = True):
        indexes = self.selectedIndexes()
        if len(indexes) != 0:
            if not self.model().isDir(indexes[0]) and not self._parser is None:
                if clear and ground:
                    self._parser.load_instance(self.model().filePath(indexes[0]))
                elif ground:
                    self._parser.parse_file(self.model().filePath(indexes[0]),
                                            clear = clear,
                                            clear_actions = clear_actions)
                else:
                    self._parser.load(self.model().filePath(indexes[0]))

    def mouseClickEvent (self, event):
        self._menu.hide()
        return super(self.__class__, self).mouseDoubleClickEvent(event)

    def mouseDoubleClickEvent (self, event):
        self._load_selected()
        return super(self.__class__, self).mouseDoubleClickEvent(event)

    def keyPressEvent (self, event):
        if event.key() == Qt.Key_Return:
            self._load_selected()
        elif event.key() == Qt.Key_W:
            self.setTreePosition(self.treePosition() + 1)
        elif event.key() == Qt.Key_S:
            self.setTreePosition(self.treePosition() - 1)
        return super(self.__class__, self).keyPressEvent(event)

    def set_parser(self, parser):
        self._parser = parser

class InstanceFileBrowser(VizWidget):
    def __init__(self, directory = None):
        super(InstanceFileBrowser, self).__init__()
        self._tree_model = QFileSystemModel()
        self._tree_model.setRootPath(QDir.rootPath())

        self._tree = InstanceFileTree(self)
        self._tree.setModel(self._tree_model)
        self._tree.move(0,20)
        if directory is not None:
            self._tree.setRootIndex(self._tree_model.index(directory))
        else:
            self._tree.setRootIndex(self._tree_model.index(QDir.rootPath()))

        self._parser = None
        str_filter = configuration.config.get('visualizer', 'file_filters')
        str_filter = str_filter.replace(' ', '')
        self._tree_model.setNameFilters(str_filter.split(','))

    def resizeEvent (self, event):
        self._tree.setColumnWidth(0,self.width())
        self._tree.resize(self.width(), self.height()-20)

    def set_parser(self, parser):
        self._tree.set_parser(parser)

class TimestepWidget(QTextEdit):
    def __init__(self):
        super(self.__class__, self).__init__()
        self._model_view = None
        self.setReadOnly(True)

    def set_model_view(self, model_view):
        self._model_view = model_view
        self._model_view.get_model().add_window(self)
        self.update()

    def resizeEvent(self, event):
        font_size = min(event.size().width() / 12, event.size().height() / 2)
        if font_size > 20:
            font_size = 20
        elif font_size < 1:
            font_size = 1
        self.setFontPointSize(font_size)
        self.update()
        super(self.__class__, self).resizeEvent(event)

    def update(self):
        if self._model_view is None:
            return
        if self._model_view.get_model() is None:
            return
        step = self._model_view.get_model().get_current_step()
        speed_up = 1/self._model_view.get_timer_speedup()
        self.setText('current step: '
                                        + str(step)
                                        + '\nspeed: '
                                        + '%.2f' % speed_up)
        super(self.__class__, self).update()

class ControlWidget(QWidget):
    def __init__(self):
        super(self.__class__, self).__init__()

        self._model_view = None
        self._timestep_widget = None
        key_string = configuration.config.get('controls', 'do_backstep')
        self.create_button('<', (20, 0),
                            self.on_undo,
                            QKeySequence(key_string),
                            'Do one step\n[' + key_string + ']')
        key_string = configuration.config.get('controls', 'do_step')
        self.create_button('>', (100, 0),
                            self.on_update,
                            QKeySequence(key_string),
                            'Undo one step\n[' + key_string + ']')
        key_string = configuration.config.get('controls', 'pause')
        self._pause_button = self.create_button('|>', (60, 0),
                                                self.on_pause,
                                                QKeySequence(key_string),
                                                'Pause/Unpause the visualisation\n[' + key_string + ']')[0]
        key_string = configuration.config.get('controls', 'step_slow_down')
        self.create_button('|<|<', (20, 35),
                            lambda: self.on_speed_up(-0.1),
                            QKeySequence(key_string),
                            'Slow down the visualisation\n[' + key_string + ']')
        key_string = configuration.config.get('controls', 'step_speed_up')
        self.create_button('|>|>', (60, 35),
                            lambda: self.on_speed_up(0.0909),
                            QKeySequence(key_string),
                            'Speed up the visualisation\n[' + key_string + ']')
        self.create_button('|<', (100, 35),
                            self.on_restart, None,
                            'Restart the visualisation')
        self.create_button('>|', (140, 35),
                            self.on_skip_to_end, None,
                            'Skip to the end of the visualisation')

        key_string = configuration.config.get('controls', 'zoom_in')
        self.create_button('+', (20, 75),
                            lambda: self.on_zoom(100),
                            QKeySequence(key_string),
                            'Zoom in\n[' + key_string + ']')
        key_string = configuration.config.get('controls', 'zoom_out')
        self.create_button('-', (60, 75),
                            lambda: self.on_zoom(-100),
                            QKeySequence(key_string),
                            'Zoom out\n[' + key_string + ']')
        self.setFixedHeight(105)

    def create_button(self, name, pos, function, shortcut, tooltip = None):
        button = QPushButton(name, self)
        button.move(pos[0], pos[1])
        button.resize(30,30)
        button.clicked.connect(function)
        if tooltip is not None:
            button.setToolTip(tooltip)

        action = None
        if shortcut is not None:
            action = QAction(self)
            action.setShortcut(shortcut)
            action.setShortcutContext(Qt.ApplicationShortcut)
            action.triggered.connect(function)
            self.addAction(action)
        return (button, action)

    def set_model_view(self, model_view):
        self._model_view = model_view
        self._model_view.get_model().add_window(self)
        self.update()

    def set_timestep_widget(self, timestep_widget):
        self._timestep_widget = timestep_widget

    def on_update(self, event = None):
        if self._model_view is not None:
            self._model_view.stop_timer()
            self._model_view.update_model(True)

    def on_pause(self, event = None):
        if self._model_view is not None:
            self._model_view.switch_timer()
        self.update()

    def on_undo(self, event = None):
        if self._model_view is not None:
            self._model_view.stop_timer()
            self._model_view.undo_model()

    def on_speed_up(self, speed_up):
        if self._model_view is not None:
            self._model_view.speed_up_timer(speed_up)
            self._timestep_widget.update()

    def on_restart(self):
        if self._model_view is not None:
            self._model_view.get_model().restart()

    def on_skip_to_end(self):
        if self._model_view is not None:
            model = self._model_view.get_model().skip_to_end()

    def on_zoom(self, zoom):
        if self._model_view is not None:
            self._model_view.zoom_event(zoom)

    def resizeEvent(self, event):
        super(self.__class__, self).resizeEvent(event)

    def update(self):
        if self._model_view is None:
            return
        if self._model_view.get_model() is None:
            return
        if self._model_view.is_timer_running():
            self._pause_button.setText('|>')
        else:
            self._pause_button.setText('||')
        super(self.__class__, self).update()

class OccursWidget(QTextEdit):
    def __init__(self):
        super(self.__class__, self).__init__()
        self._model = None
        self.setReadOnly(True)
        self.resize(400, 400)
        self.setWindowTitle('Occurs')
        self.setFontPointSize(14)

    def update(self):
        action_lists = []
        max_len = 0
        text = ''
        scroll_bar = self.verticalScrollBar()
        pos = scroll_bar.sliderPosition()
        for agent in self._model.iterate_graphic_items():
            action_list = agent.to_occurs_str()
            if len(action_list) != 0:
                action_lists.append(action_list)
                max_len = max(max_len, len(action_list))

        join_list = []      
        for i in range(0, max_len):
            if i == self._model.get_current_step():
                join_list.append('<font color = green>')


            for action_list in action_lists:
                if len(action_list) > i:
                    if action_list[i] is not None:
                        join_list.append(action_list[i])


            if i == self._model.get_current_step():
                join_list.append('</font>')
                text = text + ''.join(join_list)
                join_list = []
                self.setHtml(text)
                self.moveCursor(QTextCursor.End)
                pos = self.verticalScrollBar().sliderPosition()
        text = text + ''.join(join_list)

        self.setHtml(text)
        scroll_bar.setSliderPosition(pos)
        super(self.__class__, self).update()

    def set_model(self, model):
        self._model = model
        if self._model is not None:
            self._model.add_window(self)

class ControlSplitter(VizWidget):
    def __init__(self):
        super(ControlSplitter, self).__init__()
        self._splitter = QSplitter(Qt.Vertical, self)
        self._timestep_widget = TimestepWidget()
        self._control_widget = ControlWidget()
        self._occurs_widget = OccursWidget()
        self._splitter.addWidget(self._timestep_widget)
        self._splitter.addWidget(self._control_widget)
        self._splitter.addWidget(self._occurs_widget)
        self._control_widget.set_timestep_widget(self._timestep_widget)
        self._splitter.setSizes([40, 105, self.size().height() - 145])
        self._splitter.show()
        self._timestep_widget.show()
        self._control_widget.show()
        self._occurs_widget.show()

    def set_model_view(self, model_view):
        self._timestep_widget.set_model_view(model_view)
        self._control_widget.set_model_view(model_view)

    def set_model(self, model):
        self._occurs_widget.set_model(model)

    def resizeEvent(self, event):
        self._splitter.resize(event.size())

class ServerDialog(QWidget):
    def __init__(self, title, host, port, socket):
        super(ServerDialog, self).__init__()

        self._socket = socket

        self.setWindowTitle(title)
        self._host_text = QLineEdit(self)
        self._host_text.setText('host: ')
        self._host_text.setReadOnly(True)
        self._port_text = QLineEdit(self)
        self._port_text.setText('port: ')
        self._port_text.setReadOnly(True)
        self._host_textbox = QLineEdit(self)
        self._host_textbox.setText(host)
        self._port_textbox = QLineEdit(self)
        self._port_textbox.setText(port)
        self._ok_button = QPushButton('Ok', self)
        self._cancel_button = QPushButton('Cancel', self)
        self._function = None

        self._ok_button.clicked.connect(self.on_ok)
        self._cancel_button.clicked.connect(self.on_cancel)
        self.setFixedSize(320, 110)
        self._host_text.resize(140, 30)
        self._port_text.resize(140, 30)
        self._host_textbox.resize(140,30)
        self._port_textbox.resize(140,30)
        self._host_text.move(0,0)
        self._port_text.move(0,40)
        self._host_textbox.move(140,0)
        self._port_textbox.move(140,40)
        self._ok_button.move(20,80)
        self._cancel_button.move(140,80)

    def set_address(self, host, port):
        self._host_textbox.setText(str(host))
        self._port_textbox.setText(str(port))

    def on_ok(self, event = None):
        try:
            if (self._socket.connect(self._host_textbox.text(),
                    int(self._port_textbox.text())) < 0):
                return
            self._socket.run()
        except(ValueError, TypeError):
            print('the port must be an integer value')
        self.hide()
    def on_cancel(self, event):
        self.hide()

class InitServerDialog(QWidget):
    def __init__(self, socket_name, command, port, socket):
        super(self.__class__, self).__init__()

        self._socket = socket

        self.setWindowTitle('Initialize ' + str(socket_name))
        self._textbox = QLineEdit(self)
        self._textbox.setText(command)

        self._port_text = QLineEdit(self)
        self._port_text.setText('port: ')
        self._port_text.setReadOnly(True)
        self._port_text.resize(140, 30)
        self._port_text.move(0,35)
        self._port_textbox = QLineEdit(self)
        self._port_textbox.setText(port)
        self._port_textbox.resize(140,30)
        self._port_textbox.move(140,35)

        self._ok_button = QPushButton('Ok', self)
        self._cancel_button = QPushButton('Cancel', self)
        self._function = None

        self._ok_button.clicked.connect(self.on_ok)
        self._cancel_button.clicked.connect(self.on_cancel)
        self.setFixedSize(320, 100)
        self._textbox.resize(280,30)
        self._ok_button.move(20,70)
        self._cancel_button.move(140,70)

    def on_ok(self, event):
        self.hide()
        try:
            self._socket.run_script(
                    self._textbox.text().replace('__dir__', os.path.dirname(sys.argv[0])),
                    int(self._port_textbox.text()))
        except(ValueError):
            print('the port must be an integer value')
    def on_cancel(self, event):
        self.hide()

class GridSizeDialog(QWidget):
    def __init__(self):
        super(self.__class__, self).__init__()

        self._model = None
        self.model_view = None
        self._item_window = None
        self.setWindowTitle('Grid size')
        self._width_text = QLineEdit(self)
        self._width_text.setText('x: ')
        self._width_text.setReadOnly(True)
        self._height_text = QLineEdit(self)
        self._height_text.setText('y: ')
        self._height_text.setReadOnly(True)
        self._width_textbox = QLineEdit(self)
        self._width_textbox.setText('0')
        self._height_textbox = QLineEdit(self)
        self._height_textbox.setText('0')
        self._checkbox = QCheckBox('enable new nodes', self)
        self._ok_button = QPushButton('Ok', self)
        self._cancel_button = QPushButton('Cancel', self)
        self._function = None

        self._ok_button.clicked.connect(self.on_ok)
        self._cancel_button.clicked.connect(self.on_cancel)
        self.setFixedSize(280, 150)
        self._width_text.resize(140, 30)
        self._height_text.resize(140, 30)
        self._width_textbox.resize(140,30)
        self._height_textbox.resize(140,30)
        self._width_text.move(0,0)
        self._height_text.move(0,40)
        self._width_textbox.move(140,0)
        self._height_textbox.move(140,40)
        self._checkbox.move(0, 80)
        self._ok_button.move(20,120)
        self._cancel_button.move(140,120)

    def set_model(self, model):
        self._model = model

    def set_model_view(self, model_view):
        self._model_view = model_view

    def on_ok(self, event):
        self.hide()
        if self._model is None:
            return
        if not self._model.get_editable():
            return
        try:
            self._model.set_grid_size(int(self._width_textbox.text()),
                                      int(self._height_textbox.text()),
                                      self._checkbox.isChecked())
        except ValueError:
            print('x and y must be interger values')
        if self._model_view is not None:
            self._model_view.update()
            self._model_view.resize_to_fit()

    def on_cancel(self, event):
        self.hide()

class OrderDialog(QWidget):
    def __init__(self):
        super(self.__class__, self).__init__()

        self._model = None
        self.setWindowTitle('Add order')
        self.setFixedSize(280, 190)

        self._id_text = QLineEdit(self)
        self._id_text.setText('order id: ')
        self._id_text.setReadOnly(True)
        self._id_text.move(0,0)
        self._id_text.resize(140, 30)
        self._id_textbox = QLineEdit(self)
        self._id_textbox.setText('0')
        self._id_textbox.move(140,0)
        self._id_textbox.resize(140,30)

        self._product_id_text = QLineEdit(self)
        self._product_id_text.setText('product id: ')
        self._product_id_text.setReadOnly(True)
        self._product_id_text.move(0,40)
        self._product_id_text.resize(140, 30)
        self._product_id_textbox = QLineEdit(self)
        self._product_id_textbox.setText('0')
        self._product_id_textbox.move(140,40)
        self._product_id_textbox.resize(140,30)

        self._product_amount_text = QLineEdit(self)
        self._product_amount_text.setText('product amount: ')
        self._product_amount_text.setReadOnly(True)
        self._product_amount_text.move(0,80)
        self._product_amount_text.resize(140, 30)
        self._product_amount_textbox = QLineEdit(self)
        self._product_amount_textbox.setText('0')
        self._product_amount_textbox.move(140,80)
        self._product_amount_textbox.resize(140,30)

        self._ps_text = QLineEdit(self)
        self._ps_text.setText('picking station id: ')
        self._ps_text.setReadOnly(True)
        self._ps_text.move(0,120)
        self._ps_text.resize(140, 30)
        self._ps_textbox = QLineEdit(self)
        self._ps_textbox.setText('0')
        self._ps_textbox.move(140,120)
        self._ps_textbox.resize(140,30)

        self._ok_button = QPushButton('Ok', self)
        self._ok_button.move(20,160)
        self._ok_button.clicked.connect(self.on_ok)
        self._cancel_button = QPushButton('Cancel', self)
        self._cancel_button.move(140,160)
        self._cancel_button.clicked.connect(self.on_cancel)

    def on_ok(self, event):
        if self._model is None:
            return
        try:
            order = self._model.get_item(item_kind = 'order',
                        ID = self._id_textbox.text(),
                        create = True,
                        add_immediately = self._model.get_editable())
            if not self._model.get_editable() and self._model.contains(order):
                print('commited orders can not be edited')
            else:
                order.set_station_id(self._ps_textbox.text())
                order.add_request(self._product_id_textbox.text(),
                                int(self._product_amount_textbox.text()))
                self._model.update_windows()
        except:
            print('failed to add new request')
            return
        self.hide()

    def on_cancel(self, event):
        self.hide()

    def set_model(self, model):
        self._model = model

class OrderTable(QTableWidget):
    def __init__(self):
        super(self.__class__, self).__init__()
        self._model = None
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(['Order ID', 'Picking Station', 'Product', 'Product Amount', 'Delivered', 'Open'])
        self.setMinimumHeight(60)

        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self._menu = QMenu()
        self._menu.setParent(self)

        self._order_dialog = OrderDialog()

    def contextMenuEvent(self, event):
        order = None
        request = None
        item = self.itemAt(event.x(), event.y())
        if item is not None:
            row = self.row(item)
            count = 0
            for order2 in self._model.filter_items(item_kind = 'order'):
                if count <= row:
                    for request2 in order2.iterate_requests():
                        if count == row:
                            if self._model.get_editable():
                                request = request2
                                order = order2
                            count += 1
                            break
                        count += 1

            if count <= row:
                for order2 in self._model.filter_items(
                                    item_kind = 'order',
                                    return_non_buffered = False,
                                    return_buffered = True):
                    if count <= row:
                        for request2 in order2.iterate_requests():
                            if count == row:
                                request = request2
                                order = order2
                                break
                            count += 1

        self._menu.clear()
        action = QAction('add order', self)
        action.setShortcut('Ctrl + O')
        action.setStatusTip('Adds a new order')
        action.triggered.connect(self.add_order)
        self._menu.addAction(action)

        if request is not None:
            action = QAction('remove request', self)
            action.setShortcut('Ctrl + R')
            action.setStatusTip('Removes the selected request')
            action.triggered.connect(lambda: self.remove_request(order, request.product_id))
            self._menu.addAction(action)

        if order is not None:
            action = QAction('remove order', self)
            action.setShortcut('Ctrl + O')
            action.setStatusTip('Removes the selected order')
            action.triggered.connect(lambda: self.remove_order(order))
            self._menu.addAction(action)

        self._menu.popup(QPoint(event.x(),event.y()))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton or event.button() == Qt.MiddleButton:
            self._menu.hide()
        super(self.__class__, self).mousePressEvent(event)

    def set_model(self, model):
        self._model = model
        self._order_dialog.set_model(model)

    def add_order(self):
        self._menu.hide()
        self._order_dialog.show()

    def remove_order(self, order):
        self._menu.hide()
        self._model.remove_item(order)
        self._model.update_windows()

    def remove_request(self, order, product_id):
        self._menu.hide()
        order.remove_request(product_id)
        if order.get_num_requests() == 0:
            self._model.remove_item(order)
        self._model.update_windows()

class VizTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            return int(self.text()) < int(other.text())
        except:
            return super(VizTableWidgetItem, self).__lt__(other)

class OrderWidget(VizWidget):
    def __init__(self):
        super(self.__class__, self).__init__()
        self._splitter = QSplitter(Qt.Vertical, self)
        self._model = None
        self._table = OrderTable()
        self._table.setSortingEnabled(True)
        self.setWindowTitle('Orders')
        self._do_update = False
        self._splitter.addWidget(self._table)

        self._control_widget = QWidget()
        self._splitter.addWidget(self._control_widget)
        self._control_widget.setFixedHeight(24)

        self._deliver_widget = QTextEdit()
        self._deliver_widget.setReadOnly(True)
        self._splitter.addWidget(self._deliver_widget)

        self._table.itemChanged.connect(self.changed_item)

        self._send_button = QPushButton('Send orders', self._control_widget)
        self._send_button.move(20,0)
        self._send_button.clicked.connect(self.on_send)
        self._discard_button = QPushButton('Discard orders', self._control_widget)
        self._discard_button.move(140,00)
        self._discard_button.clicked.connect(self.on_discard)

    def update(self):
        self._deliver_widget.clear()
        orders = self._model.filter_items(item_kind = 'order')
        orders2 = self._model.filter_items(item_kind = 'order',
                        return_non_buffered = False,
                        return_buffered = True)
        for order in orders:
            for ss in order.to_delivered_str():
                self._deliver_widget.append(ss)

        red_brush   = QBrush(QColor(200, 100, 100))
        white_brush = QBrush(QColor(255, 255, 255))
        yellow_brush = QBrush(QColor(255, 255, 100))

        count = 0
        self._do_update = True
        self._table.setSortingEnabled(False)
        for order in orders:
            for request in order.iterate_requests():
                count = count + 1
        for order in orders2:
            for request in order.iterate_requests():
                count = count + 1

        if self._model.get_editable() or self._table.rowCount() != count:
            changed_requests = False
        else:
            changed_requests = True
        self._table.setRowCount(count)

        count = 0
        for order in orders:
            for request in order.iterate_requests():
                item = self._table.item(count, 0)
                if item is not None:
                    if request.changed:
                        for ii in range(0, self._table.columnCount()):
                           self._table.item(count, ii).setBackground(red_brush)
                    else:
                        for ii in range(0, self._table.columnCount()):
                            self._table.item(count, ii).setBackground(white_brush)

                self.set_item_text(count, 0, str(order.get_id()))
                self.set_item_text(count, 1, str(order.get_station_id()))
                self.set_item_text(count, 2, str(request.product_id))
                self.set_item_text(count, 3, str(request.requested))
                self.set_item_text(count, 4, str(request.delivered))
                self.set_item_text(count, 5, str(request.requested - request.delivered))
                count = count + 1

        for order in orders2:
            for request in order.iterate_requests():

                self.set_item_text(count, 0, str(order.get_id()), True)
                self.set_item_text(count, 1, str(order.get_station_id()), True)
                self.set_item_text(count, 2, str(request.product_id), True)
                self.set_item_text(count, 3, str(request.requested), True)
                self.set_item_text(count, 4, str(request.delivered), True)
                self.set_item_text(count, 5, str(request.requested - request.delivered), True)

                for ii in range(0, self._table.columnCount()):
                    self._table.item(count, ii).setBackground(yellow_brush)

                count = count + 1
        self._table.setSortingEnabled(True)
        self._do_update = False
        super(self.__class__, self).update()

    def set_item_text(self, column, row, text, editable = False):
        item = self._table.item(column, row)
        if item is None:
            self._table.setItem(column, row, VizTableWidgetItem(text))
            item = self._table.item(column, row)
        else:
            item.setText(text)

        if (row == 1 or row == 3) and (self._model.get_editable() or editable):
            item.setFlags(Qt.ItemIsSelectable |  Qt.ItemIsEnabled | Qt.ItemIsEditable)
        else:
            item.setFlags(Qt.ItemIsSelectable |  Qt.ItemIsEnabled)

    def set_model(self, model):
        self._model = model
        if self._model is not None:
            self._model.add_window(self)
        self._table.set_model(model)

    def on_send(self):
        if self._model is None:
            return
        self._model.accept_new_items(['order'])
        self.update()

    def on_discard(self):
        if self._model is None:
            return
        self._model.discard_new_items(['order'])
        self.update()

    def resizeEvent(self, event):
        self._splitter.resize(event.size().width(), event.size().height())

    def changed_item(self, item):
        if self._do_update:
            return

        value = 0
        order_id = self._table.item(item.row(), 0).text()
        column = item.column()
        order = self._model.get_item('order', order_id)
        if order is None:
            return
        try:
            value = int(item.text())
        except ValueError as err:
            print(err)
            self.update()
            return

        if column == 1:
            order.set_station_id(value)
        elif column == 3:
            order.set_requested_amount(self._table.item(item.row(), 2).text(), value)
        self.update()

class ProductDialog(QWidget):
    def __init__(self):
        super(self.__class__, self).__init__()

        self._shelf = None
        self._product_window = None
        self.setWindowTitle('Add product')
        self._id_text = QLineEdit(self)
        self._id_text.setText('product id: ')
        self._id_text.setReadOnly(True)
        self._count_text = QLineEdit(self)
        self._count_text.setText('product count: ')
        self._count_text.setReadOnly(True)
        self._id_textbox = QLineEdit(self)
        self._id_textbox.setText('0')
        self._count_textbox = QLineEdit(self)
        self._count_textbox.setText('0')
        self._ok_button = QPushButton('Ok', self)
        self._cancel_button = QPushButton('Cancel', self)
        self._function = None

        self._ok_button.clicked.connect(self.on_ok)
        self._cancel_button.clicked.connect(self.on_cancel)
        self.setFixedSize(320, 110)
        self._id_text.resize(140, 30)
        self._count_text.resize(140, 30)
        self._id_textbox.resize(140,30)
        self._count_textbox.resize(140,30)
        self._id_text.move(0,0)
        self._count_text.move(0,40)
        self._id_textbox.move(140,0)
        self._count_textbox.move(140,40)
        self._ok_button.move(20,80)
        self._cancel_button.move(140,80)

    def set_shelf(self, shelf):
        self._shelf = shelf

    def set_product_window(self, product_window):
        self._product_window = product_window

    def on_ok(self, event):
        self.hide()
        if self._shelf is None:
            return
        try:
            self._shelf.add_product(int(self._id_textbox.text()), int(self._count_textbox.text()))
        except ValueError:
            print('the product id and the product counts must be integer values')
        self._product_window.update()

    def on_cancel(self, event):
        self.hide()

class ProductWindow(VizWidget):
    def __init__(self):
        super(ProductWindow, self).__init__()
        self._table = ProductTable()
        self._table.setParent(self)
        self._table.move(0, 20)

    def set_model(self, model):
        self._table.set_model(model)

    def update(self):
        self._table.update()

    def resizeEvent(self, event):
        self._table.resize(event.size().width(), event.size().height() - 20)

class ProductTable(QTreeWidget):
    def __init__(self):
        super(ProductTable, self).__init__()
        self._model = None
        self.setWindowTitle('Products')

        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self._menu = QMenu()
        self._menu.setParent(self)
        self._product_dialog = ProductDialog()
        self._product_dialog.set_product_window(self)
        self.setHeaderLabels(['product ID', 'count', 'removed'])
        self.resize(400, 200)

    def set_model(self, model):
        self._model = model
        self.update()
        if self._model is not None:
            self._model.add_window(self)

    def update(self):
        if self._model == None:
            return
        expanded_items = []
        for ii in range(0, self.topLevelItemCount()):
            item = self.topLevelItem(ii)
            if item.isExpanded():
                expanded_items.append(ii)

        self.clear()

        for shelf in self._model.filter_items(item_kind = 'shelf'):
            tree_item = QTreeWidgetItem(['Shelf(' + str(shelf.get_id()) + ')'])
            self.addTopLevelItem(tree_item)
            for product in shelf.iterate_products():
                temp_item = QTreeWidgetItem([str(product[0]), str(product[1]), str(product[2])])
                tree_item.addChild(temp_item)
        for item in expanded_items:
            self.expandItem(self.topLevelItem(item))

    def show(self):
        self.update()
        return super(self.__class__, self).show()

    def contextMenuEvent(self, event):

        if not self._model.get_editable():
            return
        item = self.itemAt(event.x(),event.y())
        if item is None:
            return
        parent = item.parent()

        #find the shelf_index
        shelf_index = 0
        shelf = None
        if parent is None:
            shelf_index = self.indexOfTopLevelItem(item)
        else:
            shelf_index = self.indexOfTopLevelItem(parent)

        #get the shelf
        count = 0
        for shelf2 in self._model.filter_items(item_kind = 'shelf'):
            if count == shelf_index:
                shelf = shelf2
                break
            else:
                count = count + 1

        self._menu.clear()
        if parent is not None:

            #get the product_id
            product_id = 0
            count = 0
            for product in shelf.iterate_products():
                if count == parent.indexOfChild(item):
                    product_id = product[0]
                    break
            else:
                count = count + 1

            action = QAction('remove product', self)
            action.setShortcut('Ctrl + R')
            action.setStatusTip('Removes a product from the selected shelf')
            action.triggered.connect(lambda: self.delete_product(shelf, product_id))
            self._menu.addAction(action)

        action = QAction('add product', self)
        action.setShortcut('Ctrl + A')
        action.setStatusTip('Adds a product to the selected shelf')
        action.triggered.connect(lambda: self.add_product(shelf))
        self._menu.addAction(action)

        self._menu.popup(QPoint(event.x(),event.y()))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton or event.button() == Qt.MiddleButton:
            self._menu.hide()
        super(self.__class__, self).mousePressEvent(event)

    def add_product(self, shelf):
        self._product_dialog.set_shelf(shelf)
        self._menu.hide()
        self._product_dialog.show()

    def delete_product(self, shelf, product_id):
        shelf.delete_product(product_id)
        self._menu.hide()
        self.update()

class TaskTable(QTableWidget):
    def __init__(self):
        super(self.__class__, self).__init__()
        self._model = None
        self.setWindowTitle('Tasks')
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(['Task ID', 'Task Group',
                                        'Task Type', 'Assigned Robot',
                                        'Checkpoint History', 'Open Checkpoints'])
        self.setSortingEnabled(True)
        self.resizeColumnsToContents()
        self.resize(self.horizontalHeader().length() + 20, 200)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def update(self):
        tasks = self._model.filter_items(item_kind = 'task')
        red_brush   = QBrush(QColor(200, 100, 100))
        white_brush = QBrush(QColor(255, 255, 255))
        yellow_brush = QBrush(QColor(255, 255, 100))

        changed_tasks = True
        if self._model.get_editable() or self.rowCount() != len(tasks):
            changed_tasks = False

        self.setRowCount(len(tasks))

        count = 0
        self.setSortingEnabled(False)
        for task in tasks:
            task_history = ''
            task_open = ''

            for checkpoint in task.get_checkpoint_history():
                task_history = task_history + str(checkpoint) + ', '

            for checkpoint in task.get_open_checkpoints():
                task_open = task_open + str(checkpoint) + ', '

            table_item = self.item(count, 0)
            if (table_item is not None):
                if (task.get_changed() and changed_tasks):
                    for ii in range(0, self.columnCount()):
                        self.item(count, ii).setBackground(red_brush)
                else:
                    for ii in range(0, self.columnCount()):
                        self.item(count, ii).setBackground(white_brush)

            self.set_item_text(count, 0, str(task.get_id()))
            self.set_item_text(count, 1, str(task.get_task_group()))
            self.set_item_text(count, 2, str(task.get_task_type()))
            self.set_item_text(count, 3, str(task.get_robot_id()))
            self.set_item_text(count, 4, task_history)
            self.set_item_text(count, 5, task_open)
            count += 1
        self.setSortingEnabled(True)
        super(self.__class__, self).update()

    def set_item_text(self, column, row, text):
        item = self.item(column, row)
        if item is None:
            self.setItem(column, row, VizTableWidgetItem(text))
            item = self.item(column, row)
            item.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )
        else:
            item.setText(text)

    def set_model(self, model):
        self._model = model
        if self._model is not None:
            self._model.add_window(self)

class ProgramEntry(object):
    def __init__(self, program_name, short_program_name):
        self.program_name = program_name;
        self.short_program_name = short_program_name;
        self.text_field = None;

class ParserWidget(VizWidget):
    def __init__(self):
        super(self.__class__, self).__init__()
        self._splitter = QSplitter(Qt.Vertical, self)
        self._splitter.move(0, 20)
        self._button_widget = QWidget(self._splitter)
        text_splitter = QSplitter(Qt.Horizontal, self._splitter)
        self.setWindowTitle('Parser')
        self._program_tab = QTabWidget(text_splitter)
        self._program_list = []
        self._atom_text = QTextEdit(text_splitter)
        self._atom_text.setReadOnly(True)
        self._parser = None
        self._changed = False

        self._reset_grounder_button = QPushButton('reset actions', self._button_widget)
        self._reset_grounder_button.move(0,5)
        self._reset_grounder_button.resize(140,30)
        self._reset_grounder_button.clicked.connect(self.reset_actions)

        self._reset_model_button = QPushButton('reset model', self._button_widget)
        self._reset_model_button.move(140,5)
        self._reset_model_button.resize(140,30)
        self._reset_model_button.clicked.connect(self.reset_model)

        self._reset_grounder_button = QPushButton('reset grounder', self._button_widget)
        self._reset_grounder_button.move(280,5)
        self._reset_grounder_button.resize(140,30)
        self._reset_grounder_button.clicked.connect(self.reset_grounder)

        self._reset_program_button = QPushButton('reload program', self._button_widget)
        self._reset_program_button.move(420,5)
        self._reset_program_button.resize(140,30)
        self._reset_program_button.clicked.connect(self.reset_program)

        self._reset_program_button = QPushButton('delete programs', self._button_widget)
        self._reset_program_button.move(560,5)
        self._reset_program_button.resize(140,30)
        self._reset_program_button.clicked.connect(self.reset_programs)

        self._parse_program_button = QPushButton('parse programs', self._button_widget)
        self._parse_program_button.move(0,35)
        self._parse_program_button.resize(140,30)
        self._parse_program_button.clicked.connect(self.parse_program)

        self._parse_program_button = QPushButton('delete program', self._button_widget)
        self._parse_program_button.move(140,35)
        self._parse_program_button.resize(140,30)
        self._parse_program_button.clicked.connect(self.delete_program)

        self._parse_program_button = QPushButton('add empty program', self._button_widget)
        self._parse_program_button.move(280,35)
        self._parse_program_button.resize(140,30)
        self._parse_program_button.clicked.connect(self.add_empty_program)

        self._button_widget.setFixedHeight(70)

        self.move(0,0)
        self.resize(700,600)
        self._splitter.setSizes([70, 530])

    def resizeEvent(self, event):
        self._splitter.resize(event.size().width(), event.size().height())

    def set_parser(self, parser):
        if parser is self._parser:
            return
        temp = self._parser
        self._parser = parser
        if temp is not None:
            temp.set_parser_widget(None)
        if parser is not None:
            parser.set_parser_widget(self)

    def changed(self):
        self._changed = True

    def reset_actions(self):
        if self._parser is None:
            return
        self._parser.clear_model_actions()

    def reset_model(self):
        if self._parser is None:
            return
        self._parser.clear_model()

    def reset_grounder(self):
        if self._parser is None:
            return
        self.commit_programs()
        self._parser.reset_grounder()

    def reset_program(self):
        if self._parser is None:
            return
        index = self._program_tab.currentIndex()
        if index >= 0:
            self.commit_programs()
            entry = self._program_list[index]
            self._parser.load(entry.program_name)

    def reset_programs(self):
        if self._parser is None:
            return
        self._parser.reset_programs()

    def parse_program(self):
        if self._parser is None:
            return
        self.commit_programs()
        self._parser.parse()

    def delete_program(self):
        if self._parser is None:
            return
        index = self._program_tab.currentIndex()
        if index >= 0:
            entry = self._program_list[index]
            self._parser.delete_program(entry.program_name)

    def commit_programs(self):
        if not self._changed or self._parser is None:
            return
        for entry in self._program_list:
            self._parser.set_program(entry.program_name,
                                     entry.text_field.toPlainText())
    def add_empty_program(self):
        if self._parser is None:
            return
        self._parser.add_program('new', '')

    def update(self):
        if self._parser is None:
            return

        add_entrys = [];
        delete_entrys = [];

        current = self._program_tab.currentWidget()
        for entry in self._program_list:
            delete_entrys.append(entry)

        for program_name in self._parser.list_programs():
            found = False
            for entry in self._program_list:
                if entry.program_name == program_name:
                    delete_entrys.remove(entry)
                    found = True
                    break
            if not found:
                add_entrys.append(program_name)

        for entry in delete_entrys:
            self._program_list.remove(entry)
        self._program_tab.clear()

        for entry in add_entrys:
            index = entry.rfind('/') + 1
            short_program_name = entry[index :]
            count = 1
            suffix = ''
            for entry2 in self._program_list:
                if short_program_name + suffix == entry2.short_program_name:
                    count += count
                    suffix = '(' + str(count) + ')'
            short_program_name += suffix
            self._program_list.append(ProgramEntry(entry, short_program_name))

        count = 0
        for program in self._program_list:
            if program.text_field is None:
                program.text_field = QTextEdit()
                program.text_field.textChanged.connect(self.changed)
            self._program_tab.addTab(program.text_field, program.short_program_name)
            self._program_tab.setTabToolTip(count, program.program_name)
            program.text_field.setText(self._parser.get_program(program.program_name))
            count += 1

        self._atom_text.setText(self._parser.get_str_model())
        self._edited = False

        index = self._program_tab.indexOf(current)
        if index != -1:
            self._program_tab.setCurrentIndex(index)

class EnablePathWidget(QScrollArea):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setWindowTitle('Paths')
        self._model = None
        self.resize(280, 100)

        self._area = QWidget()
        self.setWidget(self._area)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._checkboxes = {}
        self._colors = {}

        self._enable_all_button = QPushButton('enable all', self._area)
        self._disable_all_button = QPushButton('disable all', self._area)
        self._enable_all_button.move(5, 5)
        self._disable_all_button.move(140, 5)
        self._enable_all_button.clicked.connect(lambda: self.on_enable_all(True))
        self._disable_all_button.clicked.connect(lambda: self.on_enable_all(False))

        self._ok_button = QPushButton('Ok', self._area)
        self._cancel_button = QPushButton('Cancel', self._area)

        self._ok_button.clicked.connect(self.on_ok)
        self._cancel_button.clicked.connect(self.on_cancel)

    def update(self):
        if self._model is None:
            return
        robots = self._model.filter_items(item_kind = 'robot')
        for key in self._checkboxes:
            self._checkboxes[key].setParent(None)
        for key in self._colors:
            self._colors[key].setParent(None)
        self._checkboxes = {}
        self._colors = {}
        y_pos = 30
        for robot in robots:
            checkbox = QCheckBox("robot" + "(" + robot.get_id() + ")", self._area)
            checkbox.move(5, y_pos)
            checkbox.setChecked(robot.get_draw_path())
            checkbox.show()
            self._checkboxes[robot.get_id()] = checkbox
            
            color_text = QTextEdit(self._area)
            color_text.setHtml('<font color = ' + robot.get_color().name() + '>' + robot.get_color().name() + '</font>')
            color_text.move(125, y_pos)
            color_text.setReadOnly(True)
            color_text.resize(160, 30)
            color_text.show()
            self._colors[robot.get_id()] = color_text
            y_pos += 40

        self._ok_button.move(5, y_pos)
        self._cancel_button.move(140, y_pos)
        self._area.resize(240, y_pos + 40)
        super(self.__class__, self).update()

    def on_enable_all(self, enable):
        for key in self._checkboxes:
            self._checkboxes[key].setChecked(enable)

    def on_ok(self):
        for key in self._checkboxes:
            robot = self._model.get_item(item_kind = 'robot', ID = key)
            if robot is not None:
                robot.set_draw_path(self._checkboxes[key].isChecked())
        self.hide()

    def on_cancel(self):
        self.hide()

    def set_model(self, model):
        self._model = model
        if self._model is not None:
            self._model.add_window(self)
        self.update()

class RobotMonitor(VizWidget):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setWindowTitle('Robot Monitor')
        self._robot = None
        self._model = None
        self._robot_textbox = QLineEdit('robot: ', self)
        self._robot_textbox.move(5,5)
        self._robot_textbox.setReadOnly(True)
        self._robot_box = QComboBox(self)
        self._robot_box.move(200,5)
        self._robot_box.activated.connect(self.on_activated)

        self._actions = QLineEdit('actions: ', self)
        self._actions.setReadOnly(True)
        self._actions.move(5, 35)
        self._position = QLineEdit('position: ', self)
        self._position.setReadOnly(True)
        self._position.move(5, 65)
        self._next_action = QLineEdit('next action: ', self)
        self._next_action.setReadOnly(True)
        self._next_action.move(5, 95)
        self._next_action.resize(400, 24)

        self._robot_actions = QTextEdit(self)
        self._robot_actions.move(5, 125)
        self._robot_actions.setReadOnly(True)
        self._robot_actions.resize(400, 200)

    def update(self):
        index = self._robot_box.currentIndex()
        self._robot_box.clear()
        if self._model is not None:
            for robot in self._model.filter_items(item_kind = 'robot'):
                self._robot_box.addItem(robot.get_id())
        self._robot_box.setCurrentIndex(index)    

        if self._robot is None:
            return
        action_list = self._robot.to_occurs_str()
        join_list = []
        cc = 0
        current_step = self._model.get_current_step()
        next_action = None
        action_count = 0
        for action in action_list:
            if action is not None:
                action_count += 1
                if cc == current_step:
                    join_list.append('<font color = green>')
                    join_list.append(action)
                    join_list.append('</font>')
                else:
                    if cc > current_step and next_action is None:
                        next_action = action
                    join_list.append(action)
            cc += 1
        self._robot_textbox.setText('robot: ' + self._robot.get_id())
        self._actions.setText('actions: ' + str(action_count) + '/' + str(self._model.get_num_steps()))
        self._position.setText('position: ' + str(self._robot.get_position()[0]) + ', ' + str(self._robot.get_position()[1]))
        if next_action is not None:
            self._next_action.setText('next action: ' + next_action)
        else:
            self._next_action.setText('next action: None')
        self._robot_actions.setHtml('\n'.join(join_list))

    def on_activated(self, text):
        robot = self._model.get_item(item_kind = 'robot', ID = self._robot_box.currentText())
        self.set_robot(robot)

    def set_robot(self, robot):
        self._robot = robot
        self.update()

    def set_model(self, model):
        self._model = model
        if self._model is not None:
            self._model.add_window(self)
        self.update()

class RobotTable(VizWidget):
    def __init__(self):
        super(RobotTable, self).__init__()
        self._table = QTableWidget(self)
        self._table.move(0, 20)
        self.setWindowTitle('Robot Table')
        self._model = None
        self._table.setColumnCount(10)
        self._table.setHorizontalHeaderLabels(['Robot ID', 'Position', 
                                               'Action number', 'Action count', 
                                               'Idle count', 'Current action', 
                                               'Next action', 'Carries', 
                                               'Current Energy', 'Max Energy'])
        self._table.itemSelectionChanged.connect(self.on_selection_changed)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table_items = {}
        self.resize(200,200)

    def update(self):
        self._table.setSortingEnabled(False)
        red_brush   = QBrush(QColor(200, 100, 100))
        green_brush = QBrush(QColor(100, 200, 100))
        white_brush = QBrush(QColor(255, 255, 255))
        blue_brush  = QBrush(QColor(155, 155, 255))
        orange_brush = QBrush(QColor(255, 128, 0))
        ignore_first = 1
        if self._model is None:
            return
        count = 0
        robots = self._model.filter_items(item_kind = 'robot')
        if(len(robots) != self._table.rowCount()):
            self._table.clearSelection()
            self._table_items = {}
            self._table.setRowCount(len(robots))
        current_step = self._model.get_current_step()
        for robot in robots:
            cc = 0
            action_count = 0
            current_action_num = 0
            idle_count = 0
            next_action = None
            current_action =  None
            for action in robot.to_occurs_str():
                if action is not None:
                    if cc == 0:
                        ignore_first = 0
                    action_count += 1
                    if cc <= current_step:
                        current_action_num += 1
                else:
                    idle_count += 1
                if cc == current_step:
                    current_action = action
                elif cc > current_step and next_action is None:
                    next_action = action
                cc += 1

            if robot.get_state() & VIZ_STATE_DELIVER:
                brush = red_brush
            elif(robot.get_current_energy() < 0 or 
                (robot.get_current_energy() > robot.get_max_energy() and 
                 robot.get_max_energy() > 0)):

                brush = orange_brush
            elif current_action is not None:
                brush = green_brush
            elif next_action is None:
                brush = blue_brush
            else:
                brush = white_brush

            self.set_item_text(count, 0, robot.get_id(), brush)
            self.set_item_text(count, 1, str(robot.get_position()[0]) + ', ' + str(robot.get_position()[1]), brush)
            self.set_item_text(count, 2, str(current_action_num), brush)
            self.set_item_text(count, 3, str(action_count), brush)
            self.set_item_text(count, 4, str(idle_count - ignore_first), brush)
            if current_action is not None:
                self.set_item_text(count, 5, current_action, brush)
            else:
                self.set_item_text(count, 5, None, brush)
            if next_action is not None:
                self.set_item_text(count, 6, next_action, brush)
            else:
                self.set_item_text(count, 6, None, brush)
            if robot.get_carries() is not None:
                self.set_item_text(count, 7, robot.get_carries().get_id(), brush)
            else:
                self.set_item_text(count, 7, "None", brush)
            self.set_item_text(count, 8, str(robot.get_current_energy()), brush)
            self.set_item_text(count, 9, str(robot.get_max_energy()), brush)
            count += 1
        self._table.setSortingEnabled(True)
        super(self.__class__, self).update()

    def on_selection_changed(self):
        robot_ids = []
        rows = []
        for index in self._table.selectedIndexes():
            row = index.row()
            if row not in rows:
                rows.append(row)
        for row in rows:
            robot_ids.append(self._table.item(row, 0).text())
        robots = self._model.filter_items(item_kind = 'robot')
        for robot in robots:
            if robot.get_id() in robot_ids:
                robot_ids.remove(robot.get_id())
                robot.set_highlighted(True)
            else:
                robot.set_highlighted(False)
        self._model.update_windows()

    def set_item_text(self, column, row, text, brush):
        if not row in self._table_items:
            self._table_items[row] = {}
        if not column in self._table_items[row]:
            self._table_items[row][column] = VizTableWidgetItem(text)
            self._table.setItem(column, row, self._table_items[row][column])
        self._table_items[row][column].setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )
        self._table_items[row][column].setBackground(brush)
        self._table_items[row][column].setText(text)

    def set_model(self, model):
        self._model = model
        if self._model is not None:
            self._model.add_window(self)
        self.update()

    def resizeEvent(self, event):
        self._table.resize(event.size().width(), event.size().height() - 20)

