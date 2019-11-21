from configparser import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
import sys

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
        self._widget = None
        self._text_edits = []

        if not os.path.isdir(os.path.expanduser('~/.config/asprilo')):
            os.makedirs(os.path.expanduser('~/.config/asprilo'))

        if not os.path.isdir(os.path.expanduser('~/.config/asprilo/visualizer')):
            os.makedirs(os.path.expanduser('~/.config/asprilo/visualizer'))

        self._file_name = os.path.expanduser('~/.config/asprilo/visualizer/init.cfg')
    
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
                        ('color', 'color_chargingstation0') : ConfigEntry(self._read_hex_from_config, 0x202020, hex, 'color charging station 1'),
                        ('color', 'color_chargingstation1') : ConfigEntry(self._read_hex_from_config, 0xff2020, hex, 'color charging station 2'),
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
                                                                            'viz-solver --port 5000 -m default -e ./encoding.lp', str,
                                                                            'solver command line'),
                        ('network', 'command_line_simulator') : ConfigEntry(self._read_str_from_config,
                                                                                'viz-simulator --port 5001 -t ./instance.lp', str,
                                                                                'simulator command line'),
                        ('visualizer', 'step_time') : ConfigEntry(self._read_int_from_config, 1200, str, 'step time'),
                        ('visualizer', 'auto_solve') : ConfigEntry(self._read_bool_from_config, False, str, 'auto solving'),
                        ('visualizer', 'create_pngs') : ConfigEntry(self._read_bool_from_config, True, str, 'create png files'),
                        ('visualizer', 'file_filters') : ConfigEntry(self._read_str_from_config, '*.lp', str, 'file browser filter'),

                        ('controls', 'step_speed_up') : ConfigEntry(self._read_str_from_config, 'Right', str, 'speed up'),
                        ('controls', 'step_slow_down') : ConfigEntry(self._read_str_from_config, 'Left', str, 'slow down'),
                        ('controls', 'do_step') : ConfigEntry(self._read_str_from_config, 'Up', str, 'do one step'),
                        ('controls', 'do_backstep') : ConfigEntry(self._read_str_from_config, 'Down', str, 'undo one step'),
                        ('controls', 'pause') : ConfigEntry(self._read_str_from_config, 'Space', str, 'pause'),
                        ('controls', 'zoom_out') : ConfigEntry(self._read_str_from_config, '-', str, 'zoom out'),
                        ('controls', 'zoom_in') : ConfigEntry(self._read_str_from_config, '+', str, 'zoom in'),
                        }
        self.read_file()

    def read_file(self):
        for key in self._values:
            if not self._config_parser.has_section(key[0]):
                self._config_parser.add_section(key[0])
            value = self._values[key]
            self._config_parser.set(key[0], key[1], 
                                    value.to_string(value.default_value))
        if self._file_name is not None:
            self._config_parser.read(self._file_name)
            with open(self._file_name, 'w') as configfile:
                self._config_parser.write(configfile)
        self.read_values()

    def set_file_name(self, file_name):
        self._file_name = file_name

    def set_value(self, section, option, value):
        try:
            self._config_parser.set(section, option, value)
            value2 = self._values[(section.lower(), option.lower())]
            value2.current_value = value
            return 0
        except:
            return -1
    
    def string_to_key(self, string):
         sequence = QKeySequence(string)

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
        self._widget = QTabWidget()
        self._widget.setWindowTitle('Settings')

        content_widget = None

        for section in self._config_parser.sections():
            y = 5
            content_widget = QWidget()
            scroll_area = QScrollArea()
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            scroll_area.setWidget(content_widget)
            self._widget.addTab(scroll_area, section)
            for option in sorted(self._config_parser.options(section)):
                if (section, option) in self._values:

                    entry = self._values[(section, option)]
                    text = QLineEdit(content_widget)
                    if entry.display_name is None:
                        text.setText(option + ':')
                    else:
                        text.setText(entry.display_name + ': ')
                    text.setReadOnly(True)
                    text.resize(240, 30)
                    text.move(0,y)

                    value_text = QLineEdit(content_widget)
                    value_text.setText(self._config_parser.get(section, option))
                    value_text.resize(240, 30)
                    value_text.move(250,y)
                    self._text_edits.append(value_text)
                    y += 35
            ok_button = QPushButton('Ok', content_widget)
            ok_button.clicked.connect(self.on_ok)
            ok_button.move(20,y)

            cancel_button = QPushButton('Cancel', content_widget)
            cancel_button.clicked.connect(self.on_cancel)
            cancel_button.move(140,y)
            content_widget.adjustSize()

        self._widget.setFixedWidth(520)

    def show_widget(self):
        if self._widget is None:
            self.create_widget()
        self._widget.show()
        
    def on_ok(self, event):
        it = iter(self._text_edits)
        for section in self._config_parser.sections():
            for option in sorted(self._config_parser.options(section)):
                if (section, option) in self._values:
                    self._config_parser.set(section, option, next(it).text())
  
        with open(self._file_name, 'w') as configfile:
            self._config_parser.write(configfile)
        self.read_values()
        self._widget.hide()

    def on_cancel(self, event):
        self._widget.hide()

    def close_widget(self):
        if self._widget is not None:
            self._widget.close()

#low level configuration
class LLConfiguration(Configuration):

    def __init__(self):
        super(self.__class__, self).__init__()
        if not os.path.isdir(os.path.expanduser('~/.config/asprilo')):
            os.makedirs(os.path.expanduser('~/.config/asprilo'))

        if not os.path.isdir(os.path.expanduser('~/.config/asprilo/visualizer')):
            os.makedirs(os.path.expanduser('~/.config/asprilo/visualizer'))

    def init_defaults(self, args = None):
        if args is None:
            return
        elif args.mode == 'complete':
            self._file_name = os.path.expanduser('~/.config/asprilo/visualizer/mcomplete.cfg')
            self._values = {
                        ('features', 'orders') : ConfigEntry(self._read_bool_from_config, True, str, 'orders'),
                        ('features', 'products') : ConfigEntry(self._read_bool_from_config, True, str, 'products'),
                        ('features', 'tasks') : ConfigEntry(self._read_bool_from_config, True, str, 'tasks'),
                        ('features', 'debug') : ConfigEntry(self._read_bool_from_config, False, str, 'debug'),
                        ('features', 'domainc') : ConfigEntry(self._read_bool_from_config, False, str, 'domainc'),
                        ('features', 'load_files') : ConfigEntry(self._read_str_from_config, '', str, 'load files'),
                        }
        elif args.mode == 'asprilo':
            self._file_name = os.path.expanduser('~/.config/asprilo/visualizer/masprilo.cfg')
            self._values = {
                        ('features', 'orders') : ConfigEntry(self._read_bool_from_config, True, str, 'orders'),
                        ('features', 'products') : ConfigEntry(self._read_bool_from_config, True, str, 'products'),
                        ('features', 'tasks') : ConfigEntry(self._read_bool_from_config, False, str, 'tasks'),
                        ('features', 'debug') : ConfigEntry(self._read_bool_from_config, False, str, 'debug'),
                        ('features', 'domainc') : ConfigEntry(self._read_bool_from_config, False, str, 'domainc'),
                        ('features', 'load_files') : ConfigEntry(self._read_str_from_config, '', str, 'load files'),
                        }
        elif args.mode == 'gtapf':
            self._file_name = os.path.expanduser('~/.config/asprilo/visualizer/mgtapf.cfg')
            self._values = {
                        ('features', 'orders') : ConfigEntry(self._read_bool_from_config, False, str, 'orders'),
                        ('features', 'products') : ConfigEntry(self._read_bool_from_config, False, str, 'products'),
                        ('features', 'tasks') : ConfigEntry(self._read_bool_from_config, True, str, 'tasks'),
                        ('features', 'debug') : ConfigEntry(self._read_bool_from_config, False, str, 'debug'),
                        ('features', 'domainc') : ConfigEntry(self._read_bool_from_config, False, str, 'domainc'),
                        ('features', 'load_files') : ConfigEntry(self._read_str_from_config,
                                                            os.path.dirname(os.path.realpath(sys.argv[0])) +  '/encodings/converter.lp',
                                                            str, 'load files'),
                        }
        self.read_file()
        self.set_value('features', 'debug', args.debug)
        self.set_value('features', 'domainc', args.domainc)

config = Configuration()
ll_config = LLConfiguration()
