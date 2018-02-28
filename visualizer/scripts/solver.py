#! /usr/bin/env python
from network import *
import os

VERSION = '0.1.1'

class Solver(Network):
    def __init__(self):
        super(Solver, self).__init__()
        self._name = 'solver'

        self._control = clingo.Control()

    def set_argument_parser_arguments(self, parser):
        super(Solver, self).set_argument_parser_arguments(parser)

    def on_data(self, data):
        if self._reset == True:
            self._control = clingo.Control()
            self._reset = False
            self._sended = - 1

        for atom in data:
            self._control.add('base', [], atom + '.')
        if self.solve() < 0:
            return
        self.send('%$RESET.')
        self.send_step(0)

    def solve(self):
        self._control.load(os.path.dirname(os.path.abspath(__file__)) + '/encodings/encoding.lp')
        self._control.ground([('base', [])])
        solve_future = self._control.solve(on_model = self.on_model, async = True)
        while(True):
            if self.is_ready_to_read():
                solve_future.cancel()
                return -1
            finished = solve_future.wait(5.0)
            if finished:
                return solve_future.get()

    def on_model(self, model):
        print 'found solution'
        self._to_send[0] = []
        for atom in model.symbols(atoms=True):
            if (atom.name == 'occurs' 
                and len(atom.arguments) == 3 
                and atom.arguments[0].name == 'object' 
                and atom.arguments[1].name == 'action'):

                self._to_send[0].append(atom)
        return True

if __name__ == "__main__":
    solver = Solver()
    solver.run()
