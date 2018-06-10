import os.path
import clingo
from . import configuration
import traceback
from .model import *

class AspParser(object):
    def __init__(self):
        self._model = Model()
        self._control = clingo.Control()
        self._model_view = None
        self._solver = None
        self._programs = {}
        self._str_model = ''
        self._parser_widget = None
        self.reset_programs()

    def set_model_view(self, model_view):
        self._model_view = model_view

    def set_solver(self, solver):
        self._solver = solver

    def set_program(self, program_name, program):
        self._programs[program_name] = program

    def add_program(self, program_name, program):
        if program_name in self._programs:
            self._programs[program_name] += program
        else:
            self._programs[program_name] = program
        if self._parser_widget is not None:
            self._parser_widget.update()

    def delete_program(self, program_name):
        if program_name in self._programs:
            del self._programs[program_name]
        if self._parser_widget is not None:
            self._parser_widget.update()

    def set_parser_widget(self, parser_widget):
        if self._parser_widget is parser_widget:
            return
        temp = self._parser_widget
        self._parser_widget = parser_widget
        if temp is not None:
            temp.set_parser(None)
        if parser_widget is not None:
            parser_widget.set_parser(self)
            parser_widget.update()

    def on_model(self, m):
        for x in m.symbols(atoms=True):
            self.on_atom(x)
            self._str_model += str(x) + '\n'
        self.done_instance()

    def on_atom(self, atom):
        if atom is None:
            return
        if len(atom.arguments) < 2:
            return
        obj = atom.arguments[0]
        value = atom.arguments[1]

        if atom.name == 'occurs' and len(atom.arguments) == 3:
            self._on_occurs_atom(obj, value, atom.arguments[2].number)
        elif atom.name == 'init' and len(atom.arguments) == 2:
            self._on_init_atom(obj, value)

    def _on_occurs_atom(self, obj, action, time_step):
        try:
            if obj.name == 'object' and action.name == 'action':

                kind = str(obj.arguments[0])
                ID = str(obj.arguments[1])

                action_name = str(action.arguments[0])
                action_value = action.arguments[1]

                item = self._model.get_item(kind, ID, True, True)
                if item is not None:
                    item.set_action(action, time_step)
                if time_step > self._model.get_num_steps(): 
                    self._model.set_num_steps(time_step)
                self._model.set_editable(False)
        except:
            print('invalid occurs format, expecting: occurs(object([object], [objectID]), action([action], [arguments]), [time step])')

    def _on_init_atom(self, obj, value):
        try:
            if (obj.name == 'object' and value.name == 'value'
                    and len(obj.arguments) == 2
                    and len(value.arguments) == 2):

                kind = str(obj.arguments[0])
                ID = str(obj.arguments[1])

                value_name = str(value.arguments[0])
                value_value = value.arguments[1]
                item = self._model.get_item(kind, ID, True, self._model.get_editable())
                if item is not None:
                    result = item.parse_init_value(value_name,
                                                    value_value)
                    if result == 0: 
                        return

                if kind == 'node' and value_name == 'at':                  #init nodes
                    self._model.add_node(value_value.arguments[0].number, 
                                         value_value.arguments[1].number, ID)
                    return

                elif kind == 'highway' and value_name == 'at':             #init highways
                    self._model.add_highway(value_value.arguments[0].number, 
                                            value_value.arguments[1].number)
                    return

                elif kind == 'product' and value_name == 'on':              #init products
                    if value_value.arguments is None:
                        shelf = self._model.get_item('shelf', value_value, True, True)
                        shelf.set_product_amount(ID, 0)
                        return
                    else:
                        shelf = self._model.get_item('shelf', value_value.arguments[0], True, True)
                        shelf.set_product_amount(ID, value_value.arguments[1].number)
                        return

                self._model.add_init('init(' + str(obj) + ', ' + str(value) + ')')

        except Exception as e:
            if ll_config.get('features', 'debug'):
                traceback.print_exc()
            print(('invalid init: init(' + str(obj) + ', ' + str(value) + ')'))

    def done_instance(self, enable_auto_solve = True):
        self._model.accept_new_items()
        self._model.update_windows()
        if (self._solver is not None
            and configuration.config.get('visualizer', 'auto_solve') 
            and enable_auto_solve):
            self._solver.set_model(self._model)
            self._solver.solve()

        if (self._model_view is not None):
            self._model_view.update()
            self._model_view.resize_to_fit()

        if self._parser_widget is not None:
            self._parser_widget.update()

    def clear_model(self):
        self._model.clear()

    def clear_model_actions(self, restart = True):
        self._model.clear_actions()
        if restart:
            self._model.restart()

    def reset_programs(self):
        self._programs = {}
        str_load_files = configuration.ll_config.get('features', 'load_files')
        try:
            str_load_files = str_load_files.replace(' ', '')
            files = str_load_files.split(',')
            for file_name in files:
                if file_name != '':
                    if os.path.isfile(file_name):
                        ff = open(file_name)
                        self._programs[file_name] = ff.read()
                        ff.close()
        except RuntimeError as error:
            print(error)
            print('file parsing failed')
            return -1
        if self._parser_widget is not None:
            self._parser_widget.update()

    def reset_grounder(self):
        self._str_model = ''
        self._control = clingo.Control()
        if self._parser_widget is not None:
            self._parser_widget.update()

    def load(self, file_name):
        if not os.path.isfile(file_name):
            print('can not open file: ', file_name)
            return -1

        print('load file: ' + file_name)
        try:
            ff = open(file_name)
            self._programs[file_name] = ff.read()
            ff.close()
            if self._parser_widget is not None:
                self._parser_widget.update()
        except RuntimeError as error:
            print(error)
            print('file loading failed')
            return -2
        return 0

    def parse(self):
        if self._control is None:        
            return
        try:
            with self._control.builder() as bb:
                for key in self._programs:
                    clingo.parse_program(self._programs[key], lambda stm: bb.add(stm))
            self._control.ground([('base', [])])
            result = self._control.solve(on_model=self.on_model)
            print(result)
        except RuntimeError as error:
            print(error)
            return -2
        return 0

    def parse_file(self, file_name, clear = False, clear_actions = False, clear_grounder = True):
        if not os.path.isfile(file_name):
            print('can not open file: ', file_name)
            return -1

        if clear:
            self.reset_programs()
            self.clear_model()

        if clear_actions:
            self.reset_programs()
            self.clear_model_actions()

        if (clear or clear_actions) and self._model_view is not None:
            self._model_view.stop_timer()

        if clear_grounder:
            self.reset_grounder()
        if self.load(file_name) < 0:
            return -1
        if self.parse() < 0:
            return -2
        return 0

    def load_instance(self, file_name, create_png = False):
        result = self.parse_file(file_name, clear = True)
        if result < 0:
            return result

        if (self._model_view is not None 
            and (configuration.config.get('visualizer', 'create_pngs') or create_png)):

            rect = self._model_view.sceneRect()
            position  = self._model_view.mapFromScene(QPoint(rect.x(), rect.y()))
            position2 = self._model_view.mapFromScene(QPoint(rect.x() + rect.width(), 
                                                            rect.y() + rect.height()))
            pixmap = self._model_view.grab(QRect(position.x(), position.y(), 
                                                position2.x() - position.x(), 
                                                position2.y() - position.y()))
            pixmap.save(file_name[0 : file_name.rfind('.')] + '.png')
        self._model.update_windows()
        return 0

    def list_programs(self):
        for key in self._programs:
            yield key

    def get_model(self):
        return self._model

    def get_program(self, program_name):
        if program_name in self._programs:
            return self._programs[program_name]
        return None

    def get_program_count(self):
        return len(self._programs)

    def get_str_model(self):
        return self._str_model
