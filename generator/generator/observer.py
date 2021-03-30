#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ground program observation for instance generator."""

from clingo import Function, Tuple

class Observer(object):
    """Ground program observer for instance generator.

    The main purpose of this observer is to analyze the grounding sizes entailed by different ASP
    program parts of the generator encoding.

    Directly adopted from clingo's test code at
    https://github.com/potassco/clingo/blob/master/app/clingo/tests/python/observer.lp

    """

    def __init__(self):
        self._delayed = []
        self._symbols = {}
        self._reified = []
        self._terms = {}
        self._elems = {}

    def __getattr__(self, name):
        assert(not name.startswith("_"))
        def caller(*args):
            self._delayed.append((name, args))
        return caller

    def _map(self, lit):
        sign = False
        if lit < 0:
            sign = True
            lit = -lit
        ret = self._symbols.get(lit, Function("__aux"))
        if sign:
            ret = Function("neg", [ret])
        return ret

    def init_program(self, incremental):
        self._reified.append(Function("init_program", [incremental]))

    def begin_step(self):
        self._reified.append(Function("begin_step", []))

    def end_step(self):
        self._reified.append(Function("end_step", []))

    def _rule(self, choice, head, body):
        head = sorted(set([self._map(atm) for atm in head]))
        body = sorted(set([self._map(lit) for lit in body]))
        self._reified.append(Function("rule", [choice, Tuple_(head), Tuple_(body)]))

    def _weight_rule(self, choice, head, lower_bound, body):
        head = sorted(set([self._map(atm) for atm in head]))
        body = sorted(set([Tuple_([self._map(lit), weight]) for lit, weight in body]))
        self._reified.append(Function("weight_rule", [choice, Tuple_(head), lower_bound, Tuple_(body)]))

    def _minimize(self, priority, literals):
        literals = sorted(set([Tuple_([self._map(lit), weight]) for lit, weight in literals]))
        self._reified.append(Function("minimize", [priority, Tuple_(literals)]))

    def _project(self, atoms):
        atoms = sorted(set([self._map(atm) for atm in atoms]))
        self._reified.append(Function("project", [Tuple_(atoms)]))

    def _output_atom(self, symbol, atom):
        self._symbols[atom] = symbol
        self._reified.append(Function("output_atom", [symbol]))

    def _output_term(self, symbol, condition):
        condition = sorted(set([self._map(lit) for lit in condition]))
        self._reified.append(Function("output_term", [symbol, Tuple_(condition)]))

    def _output_csp(self, symbol, value, condition):
        condition = sorted(set([self._map(lit) for lit in condition]))
        self._reified.append(Function("output_csp", [symbol, value, Tuple_(condition)]))

    def _external(self, atom, value):
        self._reified.append(Function("external", [self._map(atom), str(value)]))

    def _assume(self, literals):
        literals = sorted(set([self._map(lit) for lit in literals]))
        self._reified.append(Function("assume", [Tuple_(literals)]))

    def _heuristic(self, atom, type, bias, priority, condition):
        condition = sorted(set([self._map(lit) for lit in condition]))
        self._reified.append(Function("heuristic", [atom, str(type), bias, Tuple_(condition)]))

    def _acyc_edge(self, node_u, node_v, condition):
        condition = sorted(set([self._map(lit) for lit in condition]))
        self._reified.append(Function("acyc_edge", [node_u, node_v, Tuple_(condition)]))

    def theory_term_number(self, term_id, number):
        self._terms[term_id] = lambda: number

    def theory_term_string(self, term_id, name):
        self._terms[term_id] = lambda: Function(name)

    def theory_term_compound(self, term_id, name_id_or_type, arguments):
        self._terms[term_id] = lambda: Function(self._terms[name_id_or_type]().name,
                                                [self._terms[i]() for i in arguments])

    def theory_element(self, element_id, terms, condition):
        self._elems[element_id] = lambda: Function("elem",
                                                   [Tuple_([self._terms[i]() for i in terms]),
                                                    Tuple_(sorted(set([self._map(lit) for lit in condition])))])

    def _theory_atom(self, atom_id_or_zero, term_id, elements):
        self._symbols[atom_id_or_zero] = Function("theory",
                                                  [self._terms[term_id](),
                                                   Tuple_(sorted(set([self._elems[e]() for e in elements])))]);

    def _theory_atom_with_guard(self, atom_id_or_zero, term_id, elements, operator_id, right_hand_side_id):
        self._symbols[atom_id_or_zero] = Function("theory",
                                                  [self._terms[term_id](),
                                                   Tuple_(sorted(set([self._elems[e]() for e in elements]))),
                                                   self._terms[operator_id](), self._terms[right_hand_side_id]()]);

    def finalize(self):
        for name, args in self._delayed:
            if name.startswith("theory_atom"):
                getattr(self, "_" + name)(*args)
        for name, args in self._delayed:
            if not name.startswith("theory_atom"):
                getattr(self, "_" + name)(*args)
        return Context(self._reified)

class Context(object):

    def __init__(self, reified):
        self._reified = reified[:]

    def get(self):
        return self._reified
