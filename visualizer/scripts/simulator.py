#! /usr/bin/env python
from network import *
import clingo

VERSION = '0.1.2'

class Simulator(Network):
    def __init__(self):
        super(Simulator, self).__init__()
        self._name = 'simulator'

        self._control = clingo.Control()
        for file_name in self._args.templates:
            self.load(file_name)

    def set_argument_parser_arguments(self, parser):
        super(Simulator, self).set_argument_parser_arguments(parser)
        parser.add_argument('-t', '--templates',
                                help='files to load',
                                nargs='+',
                                type=str, default = '')

    def load(self, file_name):
        self._control = clingo.Control()
        self._control.load(file_name)
        self._control.ground([('base', [])])
        self._control.solve(on_model = self.on_model)

    def on_connect(self):
        self.send('%$RESET.')
        self.send_step(0)

    def on_model(self, model):
        for atom in model.symbols(atoms=True):
            if (atom.name == 'init' 
                and len(atom.arguments) == 3
                and atom.arguments[0].name == 'object'
                and atom.arguments[1].name == 'value'):
                step = 0
                try:
                    step = int(atom.arguments[2].number)
                except Exception as error:
                    print error
                    continue
                if step not in self._to_send:
                    self._to_send[step] = []
                self._to_send[step].append('init(' + str(atom.arguments[0]) + ',' 
                                                   + str(atom.arguments[1]) + ')')
            else:
                if 0 not in self._to_send:
                    self._to_send[0] = []
                self._to_send[0].append(atom)
        return True

if __name__ == '__main__':
    simulator = Simulator()
    simulator.run()
