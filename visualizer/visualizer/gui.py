from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import configuration
import os
import sys

class InstanceFileBrowser(QTreeView):
    def __init__(self, directory = None):
        super(self.__class__, self).__init__()
        self._model = QFileSystemModel()
        self._model.setRootPath(QDir.rootPath())
        self.setModel(self._model)
        if directory is not None:
            self.setRootIndex(self._model.index(directory))
        else:
            self.setRootIndex(self._model.index(QDir.rootPath()))
        self.setColumnWidth(0,self.width())

        self._parser = None
        str_filter = configuration.config.get('visualizer', 'file_filters')
        str_filter = str_filter.replace(' ', '')
        self._model.setNameFilters(str_filter.split(','))
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self._menu = QMenu()

    def _load_selected(self, clear = True, clear_actions = False, ground = True):
        indexes = self.selectedIndexes()
        if len(indexes) != 0:
            if not self._model.isDir(indexes[0]) and not self._parser is None:
                if clear and ground:
                    self._parser.load_instance(self._model.filePath(indexes[0]))
                elif ground:
                    self._parser.parse_file(self._model.filePath(indexes[0]),
                                            clear = clear,
                                            clear_actions = clear_actions)
                else:
                    self._parser.load(self._model.filePath(indexes[0]))

    def resizeEvent (self, event):
        self.setColumnWidth(0,self.width())
        return super(self.__class__, self).resizeEvent(event)

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

    def set_parser(self, parser):
        self._parser = parser

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
            action_lists.append(action_list)
            max_len = max(max_len, len(action_list))
        for i in xrange(0, max_len):
            for action_list in action_lists:
                if len(action_list) > i:
                    if action_list[i] is not None:
                        if i == self._model.get_current_step():
                            text = (text + '<font color = green>'
                                    + action_list[i]
                                    + '<br>\n' + '</font>')
                            self.setHtml(text)
                            self.moveCursor(QTextCursor.End)
                            pos = self.verticalScrollBar().sliderPosition()
                        else:
                            text = text + action_list[i] + '<br>\n'
        self.setHtml(text)
        scroll_bar.setSliderPosition(pos)
        super(self.__class__, self).update()

    def set_model(self, model):
        self._model = model
        if self._model is not None:
            self._model.add_window(self)

class ControlSplitter(QSplitter):
    def __init__(self):
        super(self.__class__, self).__init__(Qt.Vertical)
        self._timestep_widget = TimestepWidget()
        self._control_widget = ControlWidget()
        self._occurs_widget = OccursWidget()
        self.addWidget(self._timestep_widget)
        self.addWidget(self._control_widget)
        self.addWidget(self._occurs_widget)
        self._control_widget.set_timestep_widget(self._timestep_widget)
        self.setSizes([40, 105, self.size().height() - 145])

    def set_model_view(self, model_view):
        self._timestep_widget.set_model_view(model_view)
        self._control_widget.set_model_view(model_view)

    def set_model(self, model):
        self._occurs_widget.set_model(model)

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
        except(ValueError):
            print 'the port must be an integer value'
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
            print 'the port must be an integer value'
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
            print 'x and y must be interger values'
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
                print 'commited orders can not be edited'
            else:
                order.set_station_id(self._ps_textbox.text())
                order.add_request(self._product_id_textbox.text(),
                                int(self._product_amount_textbox.text()))
                self._model.update_windows()
        except:
            print 'failed to add new request'
            return
        self.hide()

    def on_cancel(self, event):
        self.hide()

    def set_model(self, model):
        self._model = model

class OrderTable(QTableWidget):
    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)
        self._model = None
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(['Order ID', 'Picking Station', 'Product', 'Product Amount', 'Delivered', 'Open'])

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

class OrderWidget(QSplitter):
    def __init__(self):
        super(self.__class__, self).__init__(Qt.Vertical)
        self._model = None
        self._table = OrderTable(self)
        self._table.setSortingEnabled(True)
        self.resize(600, 400)
        self.setWindowTitle('Orders')
        self._do_update = False

        self._control_widget = QWidget()
        self.addWidget(self._control_widget)

        self._deliver_widget = QTextEdit()
        self._deliver_widget.setReadOnly(True)
        self.addWidget(self._deliver_widget)

        self._table.itemChanged.connect(self.changed_item)

        self._send_button = QPushButton('Send orders', self._control_widget)
        self._send_button.move(20,0)
        self._send_button.clicked.connect(self.on_send)
        self._discard_button = QPushButton('Discard orders', self._control_widget)
        self._discard_button.move(140,00)
        self._discard_button.clicked.connect(self.on_discard)
        self.setSizes([self.size().height()*0.46, self.size().height()*0.08, self.size().height()*0.46])

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
                        for ii in xrange(0, self._table.columnCount()):
                           self._table.item(count, ii).setBackground(red_brush)
                    else:
                        for ii in xrange(0, self._table.columnCount()):
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

                for ii in xrange(0, self._table.columnCount()):
                    self._table.item(count, ii).setBackground(yellow_brush)

                count = count + 1
        self._table.setSortingEnabled(True)
        self._do_update = False
        super(self.__class__, self).update()

    def set_item_text(self, column, row, text, editable = False):
        item = self._table.item(column, row)
        if item is None:
            self._table.setItem(column, row, QTableWidgetItem(text))
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
            print err
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
            print 'the product id and the product counts must be integer values'
        self._product_window.update()

    def on_cancel(self, event):
        self.hide()

class ProductWindow(QTreeWidget):
    def __init__(self):                        #init item window
        super(self.__class__, self).__init__()
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
                    for ii in xrange(0, self.columnCount()):
                        self.item(count, ii).setBackground(red_brush)
                else:
                    for ii in xrange(0, self.columnCount()):
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
            self.setItem(column, row, QTableWidgetItem(text))
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

class ParserWidget(QSplitter):
    def __init__(self):
        super(self.__class__, self).__init__(Qt.Vertical)
        self._button_widget = QWidget(self)
        text_splitter = QSplitter(Qt.Horizontal, self)
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
        self.setSizes([70, 530])

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
