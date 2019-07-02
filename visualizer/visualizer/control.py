import sys
import os
import time
import argparse
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from .parser import *
from .modelView import *
from .network import *
from .gui import *
from .configuration import *

VERSION = '0.2.3'

class VisualizerWindow(QMainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()

        self._argument_parser = argparse.ArgumentParser()
        self._argument_parser.add_argument('-d', '--directory', 
                                    help='directory to load all instances from',
                                    type=str)
        self._argument_parser.add_argument('-t', '--templates',
                                    help='loads files at the start',
                                    nargs='+', 
                                    type=str, default = '')
        self._argument_parser.add_argument('-l', '--layouts',
                                    help='loads layouts at the start',
                                    nargs='+', 
                                    type=str, default = '')
        self._argument_parser.add_argument('-p', '--plans',
                                    help='loads plans at the start',
                                    nargs='+', 
                                    type=str, default = '')
        self._argument_parser.add_argument('-m', '--mode',
                                    help='loads a preset of low level settings',
                                    choices=['gtapf','asprilo', 'complete'],
                                    type=str, default = 'asprilo')
        self._argument_parser.add_argument('-s', '--start_solver',
                                    help='starts the default solver in the init file',
                                    action='store_true')
        self._argument_parser.add_argument('-i', '--start_simulator',
                                    help='starts the default simulator in the init file',
                                    action='store_true')
        self._argument_parser.add_argument('-v', '--version',
                                    help='show the current version', 
                                    action='version',
                                    version=VERSION)
        self._argument_parser.add_argument('-c', '--domainc',
                                    help='turn off the warnings for multiple actions at the same time step for deliveries',
                                    action='store_true')
        self._argument_parser.add_argument('--debug', 
                                    help='runs the visualizer in debug mode',
                                    action='store_true')
        self._args = self._argument_parser.parse_args()
        ll_config.init_defaults(self._args)

        self._asp_parser = AspParser()
        self._model = self._asp_parser.get_model()

        self._simulator_socket = SimulatorSocket()
        self._model.add_socket(self._simulator_socket)
        self._simulator_socket.set_parser(self._asp_parser)

        self._solver_socket = SolverSocket()
        self._asp_parser.set_solver(self._solver_socket)
        self._solver_socket.set_parser(self._asp_parser)
        self._solver_socket.set_model(self._model)

        self._init_gui()

        self._asp_parser.set_model_view(self._model_view)

        self.read_input()

    def _init_gui(self):
        self._splitter = QSplitter()
        self.setCentralWidget(self._splitter)

        directory = self._args.directory
        if directory is None:
            directory= os.getcwd()

        self._instance_file_browser = InstanceFileBrowser(directory)
        self._instance_file_browser.set_parser(self._asp_parser)
        self._instance_file_browser.show()

        self._splitter.addWidget(self._instance_file_browser)
        if self._args.directory is None:
            self._instance_file_browser.setVisible(False)

        self._file_dialog = QFileDialog(self, 'Open file',
                                        directory,
                                        'Lp files (*.lp);; All files (*)')

        self._model_view = ModelView()
        self._model_view.set_model(self._model)
        self._splitter.addWidget(self._model_view)

        self._connect_solver_dialog = ServerDialog('solve',
                config.get('network', 'host_solver'),
                config.get('network', 'port_solver'),
                self._solver_socket)
        self._connect_simulator_dialog = ServerDialog('simulate',
                config.get('network', 'host_simulator'),
                config.get('network', 'port_simulator'),
                self._simulator_socket)

        self._init_solver_dialog = InitServerDialog('solver',
                config.get('network', 'command_line_solver'),
                config.get('network', 'port_solver'),
                self._solver_socket)

        self._init_simulator_dialog = InitServerDialog('simulator',
                config.get('network', 'command_line_simulator'),
                config.get('network', 'port_simulator'),
                self._simulator_socket)

        self._grid_size_dialog = GridSizeDialog()
        self._grid_size_dialog.set_model(self._model)
        self._grid_size_dialog.set_model_view(self._model_view)

        self._control_splitter = ControlSplitter()
        self._control_splitter.set_model_view(self._model_view)
        self._control_splitter.set_model(self._model)
        self._splitter.addWidget(self._control_splitter)

        self._order_widget = OrderWidget()
        self._order_widget.set_model(self._model)

        self._product_window = ProductWindow()
        self._product_window.set_model(self._model)

        self._task_widget = TaskTable()
        self._task_widget.set_model(self._model)

        self._enable_path_widget = EnablePathWidget()
        self._enable_path_widget.set_model(self._model)

        self._robot_monitor = RobotMonitor()
        self._robot_monitor.set_model(self._model)

        self._robot_table = RobotTable()
        self._robot_table.set_model(self._model)

        self._splitter.setSizes([200, 600, 200])
        self._model_view.resize_to_fit()

        self._parser_widget = ParserWidget()
        self._parser_widget.set_parser(self._asp_parser)

        QToolTip.setFont(QFont('SansSerif', 10))
        self._init_menu()

        self.setWindowTitle('Visualizer')       
        self.resize(1000, 600)
        self.move(0,0)
        self.show()
        widget_manager.set_main_widget(self)

        if self._args.start_solver:
            self._init_solver_dialog.on_ok(None)

        if self._args.start_simulator:
            self._init_simulator_dialog.on_ok(None)

        for file_name in self._args.templates:
            self._asp_parser.parse_file(file_name)
        for file_name in self._args.layouts:
            self._asp_parser.parse_file(file_name)
        for file_name in self._args.plans:
            self._asp_parser.parse_file(file_name)
        self._model_view.resize_to_fit()

    def _init_menu(self):
        self.statusBar()
        menu_bar = self.menuBar()

        menu_file = menu_bar.addMenu('File')
        menu_solver = menu_bar.addMenu('Network')
        menu_windows = menu_bar.addMenu('Tools')

        #file menu
        action = QAction('New instance', self)
        action.setShortcut('Ctrl+N')
        action.setStatusTip('Create a clear instance')
        action.triggered.connect(self._model.clear)
        menu_file.addAction(action)
        self.addAction(action)

        action = QAction('Load instance', self)
        action.setShortcut('Ctrl+L')
        action.setStatusTip('Load an instance file')
        action.triggered.connect(lambda: 
                        (self.open_file_dialog(QFileDialog.AcceptOpen, 
                         self.load_instance)))
        menu_file.addAction(action)
        self.addAction(action)

        action = QAction('Load plan', self)
        action.setShortcut('Ctrl+V')
        action.setStatusTip('Load a plan file')
        action.triggered.connect(lambda: 
                        (self.open_file_dialog(QFileDialog.AcceptOpen, 
                         self.load_answer)))
        menu_file.addAction(action)
        self.addAction(action)

        action = QAction('Save instance', self)
        action.setShortcut('Ctrl+I')
        action.setStatusTip('Save the instance to a file')
        action.triggered.connect(lambda: 
                        (self.open_file_dialog(QFileDialog.AcceptSave, 
                         self.save_instance)))
        menu_file.addAction(action)
        self.addAction(action)

        action = QAction('Save plan', self)
        action.setShortcut('Ctrl+A')
        action.setStatusTip('Saves the current plan to a file')
        action.triggered.connect(lambda: 
                        (self.open_file_dialog(QFileDialog.AcceptSave, 
                         self.save_answer)))
        menu_file.addAction(action)
        self.addAction(action)

        action = QAction('Settings', self)
        action.setShortcut('Ctrl+C')
        action.setStatusTip('Show a window to change the settings')
        action.triggered.connect(config.show_widget)
        menu_file.addAction(action)
        self.addAction(action)

        action = QAction('Create all png files', self)
        action.setShortcut('Ctrl + P')
        action.setStatusTip('Creates png files from all instance files in the given directory and all sub-directories')
        action.triggered.connect(self.create_all_pictures)
        menu_file.addAction(action)

        action = QAction('Exit', self)
        action.setShortcut('Ctrl+Q')
        action.setStatusTip('Leave the application')
        action.triggered.connect(self.close)
        menu_file.addAction(action)
        self.addAction(action)

        #network menu
        action = QAction('Solve', self)
        action.setShortcut('Ctrl+E')
        action.setStatusTip('Connect the visualizer to a solver and start solving')
        action.triggered.connect((lambda: 
            self.show_server_dialog(self._connect_solver_dialog, 
            self._solver_socket)))
        menu_solver.addAction(action)
        self.addAction(action)

        action = QAction('Fast Solve', self)
        action.setShortcut('Ctrl+S')
        action.setStatusTip('Connect the visualizer to a solver and start solving')
        action.triggered.connect((lambda: 
            self.skip_server_dialog(self._connect_solver_dialog, 
            self._solver_socket)))
        menu_solver.addAction(action)
        self.addAction(action)

        action = QAction('Simulate', self)
        action.setShortcut('Ctrl+Y')
        action.setStatusTip('Connect the visualizer to a simulator')
        action.triggered.connect((lambda: 
            self.show_server_dialog(self._connect_simulator_dialog, 
            self._simulator_socket)))
        menu_solver.addAction(action)
        self.addAction(action)

        action = QAction('Fast Simulate', self)
        action.setShortcut('Ctrl+D')
        action.setStatusTip('Connect the visualizer to a simulator and start simulating')
        action.triggered.connect((lambda: 
            self.skip_server_dialog(self._connect_simulator_dialog, 
            self._simulator_socket)))
        menu_solver.addAction(action)
        self.addAction(action)

        action = QAction('Initialize solver', self)
        action.setShortcut('Ctrl+Z')
        action.setStatusTip('Run a solver script')
        action.triggered.connect(self._init_solver_dialog.show)
        menu_solver.addAction(action)

        action = QAction('Initialize simulator', self)
        action.setShortcut('Ctrl+M')
        action.setStatusTip('Run a simulator script')
        action.triggered.connect(self._init_simulator_dialog.show)
        menu_solver.addAction(action)

        #tools menu
        if ll_config.get('features', 'orders'):
            action = QAction('Orders', self)
            action.setShortcut('Ctrl+O')
            action.setStatusTip('Show a window that lists all orders')
            action.triggered.connect(lambda: self.switch_widget(self._order_widget))
            menu_windows.addAction(action)
            self.addAction(action)

        if ll_config.get('features', 'products'):
            action = QAction('Products', self)
            action.setShortcut('Ctrl+R')
            action.setStatusTip('Show a window that contains all products')
            action.triggered.connect(lambda: self.switch_widget(self._product_window))
            menu_windows.addAction(action)
            self.addAction(action)

        if ll_config.get('features', 'tasks'):
            action = QAction('Tasks', self)
            action.setShortcut('Ctrl+T')
            action.setStatusTip('Show a window that contains all tasks')
            action.triggered.connect(lambda: self.switch_widget(self._task_widget))
            menu_windows.addAction(action)
            self.addAction(action)

        action = QAction('Control', self)
        action.setShortcut('Ctrl+C')
        action.setStatusTip('Show a window to control the visualizer')
        action.triggered.connect(lambda: self.switch_widget(self._control_splitter))
        menu_windows.addAction(action)

        action = QAction('Grid size', self)
        action.setShortcut('Ctrl+G')
        action.setStatusTip('Show a window to change the grid size')
        action.triggered.connect(self._grid_size_dialog.show)
        menu_windows.addAction(action)

        action = QAction('Parser', self)
        action.setShortcut('Ctrl+P')
        action.setStatusTip('Show a window to control the parser')
        action.triggered.connect(lambda: self.switch_widget(self._parser_widget))
        menu_windows.addAction(action)
        self.addAction(action)

        action = QAction('Paths', self)
        action.setShortcut('Ctrl+W')
        action.setStatusTip('Show a window to enable and disable path drawing')
        action.triggered.connect(self._enable_path_widget.show)
        menu_windows.addAction(action)
        self.addAction(action)

        action = QAction('Robot monitor', self)
        action.setShortcut('Ctrl+M')
        action.setStatusTip('Show a window the contains information about a specific robot')
        action.triggered.connect(lambda: self.switch_widget(self._robot_monitor))
        menu_windows.addAction(action)
        self.addAction(action)

        action = QAction('Robot table', self)
        action.setShortcut('Ctrl+K')
        action.setStatusTip('Show a window the contains information about all robots')
        action.triggered.connect(lambda: self.switch_widget(self._robot_table))
        menu_windows.addAction(action)
        self.addAction(action)

        action = QAction('File browser', self)
        action.setShortcut('Ctrl+F')
        action.setStatusTip('Show a window to load files')
        action.triggered.connect(lambda: self.switch_widget(self._instance_file_browser))
        menu_windows.addAction(action)
        self.addAction(action)

    def read_input(self):
        finish_answer = False
        found_answer = False
        lines = []
        try:
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                print('Read from stdin')
                for line in sys.stdin.readlines():
                    if line.lower().find('answer') != -1:
                        found_answer = True
                    elif line.lower().find('unsatisfiable') != -1:
                        print('unsatisfiable')
                    elif line.lower().find('satisfiable') != -1:
                        print('satisfiable')
                    else:
                        lines.append(line)
                        if found_answer and not finish_answer:
                            self._asp_parser.add_program('input', line.replace(' ', '.'))
                            if line[len(line) - 1] == '\n':
                                finish_answer = True
                                self._asp_parser.add_program('input', '.')
                                self._asp_parser.parse()
                if not found_answer and len(lines) > 0:
                    self._asp_parser.add_program('input', ''.join(lines))
                    self._asp_parser.parse()
        except Exception as error:
            print(error)
            print('Failed to read from stdin')

    def switch_widget(self, widget):
        if widget.parent() is None:
            self._splitter.addWidget(widget)
            widget.resize(200, self._splitter.height())
        elif widget.isVisible():
            widget.hide()
        else:
            widget.show()

    def open_file_dialog(self, mode, function):
        self._file_dialog.setAcceptMode(mode)
        try:
            self._file_dialog.disconnect()
        except TypeError as error:
            pass
        self._file_dialog.accepted.connect(function)
        self._file_dialog.open()

    def load_instance(self):
        file_name = self._file_dialog.selectedFiles()[0]
        return self._asp_parser.load_instance(file_name)

    def load_answer(self):
        file_name = self._file_dialog.selectedFiles()[0]
        return self._asp_parser.parse_file(file_name,
                        clear = False, clear_actions = True)

    def save_instance(self):
        file_name = self._file_dialog.selectedFiles()[0]
        self._model.save_to_file(file_name)

    def save_answer(self):
        file_name = self._file_dialog.selectedFiles()[0]
        self._model.save_answer_to_file(file_name)

    def create_all_pictures(self):
        directory = str(QFileDialog.getExistingDirectory(self, 'Select directory'))
        if directory is None or len(directory) == 0: 
            return
        self.create_pictures_in_directory(directory)

    def create_pictures_in_directory(self, directory):
        for file_name in os.listdir(directory):
            full_file_name = directory + '/' + file_name
            if file_name.endswith('.lp'): 
                self._asp_parser.load_instance(full_file_name, create_png = True)
            elif os.path.isdir(full_file_name):
                self.create_pictures_in_directory(full_file_name)

    def show_server_dialog(self, dialog, server_socket):
        if server_socket.script_is_running():
            dialog.set_address(server_socket.get_host(), server_socket.get_port())
        dialog.show()

    def skip_server_dialog(self, dialog, server_socket):
        if server_socket.script_is_running():
            dialog.set_address(server_socket.get_host(), server_socket.get_port())
        dialog.on_ok()

    def exit(self):
        self._solver_socket.close()
        self._simulator_socket.close()

    def get_splitter(self):
        return self._splitter

    def closeEvent(self, event):
        self._product_window.close()
        self._order_widget.close()
        self._task_widget.close()
        self._parser_widget.close()
        self._enable_path_widget.close()
        self._robot_monitor.close()
        self._robot_table.close()
        config.close_widget()
        widget_manager.exit()
        return super(self.__class__, self).closeEvent(event)

class VizControl(object): 
    def run(self):
        app = QApplication(sys.argv)
        wnd = VisualizerWindow()
        value = app.exec_()
        wnd.exit()
        sys.exit(value)
