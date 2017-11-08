#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""XOR Count Propagator for Sampling"""

import math
import random
    
class Propagator:
    def __init__(self, s):
        self.__states = []
        self.__default_s = int(s)

    def init(self, init):
        index = 1
        literals = [init.solver_literal(atom.literal) for atom in init.symbolic_atoms.by_signature("init",2) if abs(init.solver_literal(atom.literal)) != 1]
        if len(literals) > 0:
            # Randomly create S XOR constraints
            if self.__default_s > 0:
                estimated_s = self.__default_s
            else:
                estimated_s = int(math.log(len(literals) + 1, 2))
            print "constraints: %s"%estimated_s
            for i in range(len(self.__states), init.number_of_threads):
	        self.__states.append({})
            for i in range(estimated_s):
                size = random.randint(1, (len(literals) + 1) / 2)
                lits = random.sample(literals, size)
                parity = random.randint(0,1)
                #print "constraint: %s, parity: %s"%(lits, parity)
                for thread_id in range(init.number_of_threads):
                    self.__states[thread_id].setdefault(index, []).append((lits, parity))
                index+=1
        #print self.__states

    def check(self, control):
        state = self.__states[control.thread_id]
        for id, xor in state.items():
            nogood     = []
            constraint = xor[0][0]
            parity     = xor[0][1]

            for literal in constraint:
                if control.assignment.is_true(literal):
                    nogood.append(literal)
                else:
                    nogood.append(-literal)
            if len([x for x in nogood if x > 0]) % 2 != parity:
                if not control.add_nogood(nogood) or not control.propagate():
                    return

#end.
