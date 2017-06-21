#! /usr/bin/env python
from solver import *

VERSION = '0.1.0'

class Incremental_Solver(Solver):
    def __init__(self):
        super(Incremental_Solver, self).__init__()

    def solve(self):
        self._control.load(os.path.dirname(os.path.abspath(__file__)) + '/encodings/encoding.lp')
        result = None
        step = 0

        while True:
            print 'ground: ' + str(step)
            if step == 0:
                self._control.ground([('base', []), ('init', []), 
                                      ('step', [step]),('check', [step])])
            else:
                self._control.ground([('step', [step]),('check', [step])])                
            self._control.assign_external(clingo.Function('query', [step]), True)

            print 'solve: ' + str(step)
            solve_future = self._control.solve_async(self.on_model)
            while(True):
                if self.is_ready_to_read():
                    solve_future.cancel()
                    return -1
                finished = solve_future.wait(5.0)
                if finished:
                    result = solve_future.get()
                    print result
                    break

            self._control.assign_external(clingo.Function('query', [step]), False)
            step += 1
            if not result.unsatisfiable or step > 50:
                return result

if __name__ == "__main__":
    solver = Incremental_Solver()
    solver.run()
