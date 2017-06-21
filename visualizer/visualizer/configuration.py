from ConfigParser import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os

class ConfigEntry(object):
    def __init__(self, read_value, default_value, to_string, display_name = None):
        self.default_value = default_value
        self.current_value = default_value
        self.read_value = read_value
        self.to_string = to_string
        self.display_name = display_name

class Configuration(object):
    def __init__(self, args = None):
        self._config_parser = RawConfigParser()
        self._scroll_area = None
        self._widget = None
        self._text_edits = []
        self._file_name = 'config/init.cfg'
    
        self._values = {}
        self.init_defaults()

    def init_defaults(self, args = None):
        self._values = {
                        ('color', 'color_robot0') : ConfigEntry(self._read_hex_from_config, 0xff0000, hex, 'color robot 1'),
                        ('color', 'color_robot1') : ConfigEntry(self._read_hex_from_config, 0xffff00, hex, 'color robot 2'),
                        ('color', 'color_shelf0') : ConfigEntry(self._read_hex_from_config, 0x009b00, hex, 'color shelf 1'),
                        ('color', 'color_shelf1') : ConfigEntry(self._read_hex_from_config, 0x009bff, hex, 'color shelf 2'),
                        ('color', 'color_shelf2') : ConfigEntry(self._read_hex_from_config, 0xff0000, hex, 'color carried shelf'),
                        ('color', 'color_pickingstation0') : ConfigEntry(self._read_hex_from_config, 0xffff00, hex, 'color picking station 1'),
                        ('color', 'color_pickingstation1') : ConfigEntry(self._read_hex_from_config, 0xffffff, hex, 'color picking station 2'),
                        ('color', 'color_checkpoint0') : ConfigEntry(self._read_hex_from_config, 0x006400, hex, 'color checkpoint 1'),
                        ('color', 'color_checkpoint1') : ConfigEntry(self._read_hex_from_config, 0x006464, hex, 'color checkpoint 2'),
                        ('color', 'color_checkpoint2') : ConfigEntry(self._read_hex_from_config, 0x646464, hex, 'color checkpoint 3'),
                        ('color', 'color_checkpoint3') : ConfigEntry(self._read_hex_from_config, 0x646400, hex, 'color checkpoint 4'),
                        ('color', 'color_disabled_node') : ConfigEntry(self._read_hex_from_config, 0x323232, hex, 'color disabled nodes'),
                        ('color', 'color_highway') : ConfigEntry(self._read_hex_from_config, 0x9b9bc8, hex, 'color highways'),

                        ('display', 'id_font_scale') : ConfigEntry(self._read_float_from_config, 1.0, str, 'id font scale'),
                        ('display', 'id_font_bold') : ConfigEntry(self._read_bool_from_config, False, str, 'id font bold'),
                        ('display', 'id_font_color') : ConfigEntry(self._read_hex_from_config, 0x000000, hex, 'id font color'),

                        ('network', 'port_solver') : ConfigEntry(self._read_str_from_config, '5000', str, 'solver port'),
                        ('network', 'host_solver') : ConfigEntry(self._read_str_from_config, '127.0.0.1', str, 'solver host'),
                        ('network', 'port_simulator') : ConfigEntry(self._read_str_from_config, '5001', str, 'simulator port'),
                        ('network', 'host_simulator') : ConfigEntry(self._read_str_from_config, '127.0.0.1', str, 'simulator host'),
                        ('network', 'command_line_solver') : ConfigEntry(self._read_str_from_config, 
                                                                            './solver_inc.py --port 5000', str, 
                                                                            'solver command line'),
                        ('network', 'command_line_simulator') : ConfigEntry(self._read_str_from_config, 
                                                                                './simulator.py --port 5001', str, 
                                                                                'simulator command line'),
                        ('visualizer', 'step_time') : ConfigEntry(self._read_int_from_config, 1200, str, 'step time'),
                        ('visualizer', 'auto_solve') : ConfigEntry(self._read_bool_from_config, False, str, 'auto solving'),
                        ('visualizer', 'create_pngs') : ConfigEntry(self._read_bool_from_config, True, str, 'create png files'),
                        ('visualizer', 'file_filters') : ConfigEntry(self._read_str_from_config, '*.lp', str, 'file browser filter'),
                        }
        self.read_file()

    def read_file(self):
        if not os.path.isdir('config'):
            os.makedirs('config')
        for key in self._values:
            if not self._config_parser.has_section(key[0]):
                self._config_parser.add_section(key[0])
            value = self._values[key]
            self._config_parser.set(key[0], key[1], 
                                    value.to_string(value.default_value))
        if self._file_name is not None:
            self._config_parser.read(self._file_name)
            with open(self._file_name, 'wb') as configfile:
                self._config_parser.write(configfile)
        self.read_values()

    def set_file_name(self, file_name):
        self._file_name = file_name

    def set_value(self, section, option, value):
        try:
            self._config_parser.set(section, option, value)
            value = self._values[(section.lower(), option.lower())]
            value.current_value = value
            return 0
        except:
            return -1

    def _read_str_from_config(self, section, value, default = ''):
        try: 
            return self._config_parser.get(section, value)
        except:
            return default

    def _read_hex_from_config(self, section, value, default = 0):
        try: 
            return int(self._config_parser.get(section, value),16)
        except:
            return default

    def _read_float_from_config(self, section, value, default = 0):
        try: 
            return float(self._config_parser.get(section, value))
        except:
            return default

    def _read_int_from_config(self, section, value, default = 0):
        try: 
            return self._config_parser.getint(section, value)
        except:
            return default

    def _read_bool_from_config(self, section, value, default = False):
        s = self._config_parser.get(section, value)
        if s == 'True' or s == 'true':
            return True
        if s == 'False' or s == 'false':
            return False
        else:
            return default 

    def read_values(self):
        for key in self._values:
            value = self._values[key]
            value.current_value = self.read_value(key[0], key[1])

    def read_value(self, section, option):
        value = self._values[(section, option)]
        if value is None: 
            return None
        else:
            return value.read_value(section, option, value.default_value)
        return None

    def get(self, section, option):
        try:
            value = self._values[(section.lower(), option.lower())]
        except:
            return None
        return value.current_value

    def create_widget(self):
        self._scroll_area = QScrollArea()
        self._widget = QWidget()
        self._widget.setWindowTitle('Settings')
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._scroll_area.setWidget(self._widget)

        y = 5
        for section in self._config_parser.sections():
            for option in sorted(self._config_parser.options(section)):
                if (section, option) in self._values:

                    entry = self._values[(section, option)]
                    text = QLineEdit(self._widget)
                    if entry.display_name is None:
                        text.setText(option + ':')
                    else:
                        text.setText(entry.display_name + ': ')
                    text.setReadOnly(True)
                    text.resize(200, 30)
                    text.move(0,y)

                    value_text = QLineEdit(self._widget)
                    value_text.setText(self._config_parser.get(section, option))
                    value_text.resize(200, 30)
                    value_text.move(210,y)
                    self._text_edits.append(value_text)
                    y += 35

        ok_button = QPushButton('Ok', self._widget)
        ok_button.clicked.connect(self.on_ok)
        ok_button.move(20,y)

        cancel_button = QPushButton('Cancel', self._widget)
        cancel_button.clicked.connect(self.on_cancel)
        cancel_button.move(140,y)
        self._widget.adjustSize()

    def show_widget(self):
        if self._scroll_area is None:
            self.create_widget()
        self._scroll_area.show()
        
    def on_ok(self, event):
        it = iter(self._text_edits)
        for section in self._config_parser.sections():
            for option in sorted(self._config_parser.options(section)):
                if (section, option) in self._values:
                    self._config_parser.set(section, option, it.next().text())
  
        with open(self._file_name, 'wb') as configfile:
            self._config_parser.write(configfile)
        self.read_values()
        self._scroll_area.hide()

    def on_cancel(self, event):
        self._scroll_area.hide()

#low level configuration
class LLConfiguration(Configuration):

    def __init__(self):
        super(self.__class__, self).__init__()
        self._file_name = None

    def init_defaults(self, args = None):
        if args is None:
            self._file_name = 'config/mdefault.cfg'
            self._values = {
                        ('features', 'orders') : ConfigEntry(self._read_bool_from_config, True, str, 'orders'),
                        ('features', 'products') : ConfigEntry(self._read_bool_from_config, True, str, 'products'),
                        ('features', 'tasks') : ConfigEntry(self._read_bool_from_config, True, str, 'tasks'),
                        ('features', 'debug') : ConfigEntry(self._read_bool_from_config, False, str, 'debug'),
                        ('features', 'load_files') : ConfigEntry(self._read_str_from_config, '', str, 'load files'),
                        }
        elif args.mode == 'aspilro':
            self._file_name = 'config/maspilro.cfg'
            self._values = {
                        ('features', 'orders') : ConfigEntry(self._read_bool_from_config, True, str, 'orders'),
                        ('features', 'products') : ConfigEntry(self._read_bool_from_config, True, str, 'products'),
                        ('features', 'tasks') : ConfigEntry(self._read_bool_from_config, False, str, 'tasks'),
                        ('features', 'debug') : ConfigEntry(self._read_bool_from_config, False, str, 'debug'),
                        ('features', 'load_files') : ConfigEntry(self._read_str_from_config, '', str, 'load files'),
                        }
        elif args.mode == 'gtapf':
            self._file_name = 'config/mgtapf.cfg'
            self._values = {
                        ('features', 'orders') : ConfigEntry(self._read_bool_from_config, False, str, 'orders'),
                        ('features', 'products') : ConfigEntry(self._read_bool_from_config, False, str, 'products'),
                        ('features', 'tasks') : ConfigEntry(self._read_bool_from_config, True, str, 'tasks'),
                        ('features', 'debug') : ConfigEntry(self._read_bool_from_config, False, str, 'debug'),
                        ('features', 'load_files') : ConfigEntry(self._read_str_from_config, './encodings/converter.lp', str, 'load files'),
                        }
        elif args.debug:
            self.set_value('features', 'debug', True)
        self.read_file()

config = Configuration()
ll_config = LLConfiguration()
