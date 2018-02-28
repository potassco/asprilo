#! /usr/bin/env python
from solver_inc import *

VERSION = '0.1.1'

class Interactive_Solver(Incremental_Solver):
    def __init__(self):
        super(Interactive_Solver, self).__init__()
        self._inits = []

    def on_data(self, data):
        if self._reset == True:
            self._inits = []
            self._sended = - 1
            self._to_send = {}
            self.send('%$RESET.\n')
            self._reset = False

        for atom in data:
            self._inits.append(atom)
        self._control = clingo.Control()

        for atom in self._inits:
            self._control.add('base', [], atom + '.')
        for ii in xrange(0, self._sended + 1):
            if ii in self._to_send:
                for atom in self._to_send[ii]:
                    self._control.add('base', [], str(atom) + '.')

        if self.solve() < 0:
            return
        if self._sended + 1 in self._to_send:
            self.send_step(self._sended + 1)
        elif self._sended + 2 in self._to_send:
            self.send_step(self._sended + 2)

    def on_model(self, model):
        print 'found solution'
        self._to_send = {}
        for atom in model.symbols(atoms=True):
            if (atom.name == 'occurs' 
                and len(atom.arguments) == 3 
                and atom.arguments[0].name == 'object' 
                and atom.arguments[1].name == 'action'):
                step = atom.arguments[2].number
                if step not in self._to_send:
                    self._to_send[step] = []
                self._to_send[step].append(atom)
        return True

if __name__ == "__main__":
    solver = Interactive_Solver()
    solver.run()
