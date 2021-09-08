#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ground program observation for ASPIF output of instance generator."""

from sys import getsizeof
from itertools import chain
from clingo.symbol import Function, Number, Tuple_, String

class AspifObserver(object):
    """Ground program observer for ASPIF output of instance generator.

    The main purpose of this observer is to dump ASPIF-formatted program of clingo.Control objects.
    In the context of the instance generator, this is viable for debugging and analysis.

    Mostly adopted from clingo's test code at
    https://github.com/potassco/clingo/blob/master/app/clingo/tests/python/observer.lp

    """

    def __init__(self):
        self.__delayed = []
        self.__symbols = {}
        self.__reified = []
        self.__terms = {}
        self.__elems = {}
        self.__aspif = {}

    def __getattr__(self, name):
        assert(not name.startswith("_"))
        def caller(*args):
            self.__delayed.append((name, args))
        return caller

    def __map(self, lit):
        sign = False
        if lit < 0:
            sign = True
            lit = -lit
        ret = self.__symbols.get(lit, Function("__aux"))
        if sign:
            ret = Function("neg", [ret])
        return ret

    def init_program(self, incremental):
        self.__reified.append(Function("init_program", [Number(incremental)]))

    def begin_step(self):
        self.__reified.append(Function("begin_step", []))

    def _rule(self, choice, head, body):
        """Customized for aspif output."""
        head = [1 if choice else 0, len(head)] + head
        body = [0, len(body)] + body
        self.__aspif.setdefault(1, []).append(head + body)

    def _weight_rule(self, choice, head, lower_bound, body):
        """Customized for aspif output."""
        head = [1 if choice else 0, len(head)] + head
        body = [1, lower_bound, len(body)] + list(chain.from_iterable(body))
        self.__aspif.setdefault(1, []).append(head + body)

    def _minimize(self, priority, literals):
        """Customized for aspif output."""
        self.__aspif.setdefault(2, []).append([priority, len(literals)] + list(chain.from_iterable(literals)))

    def _project(self, atoms):
        """Customized for aspif output."""
        self.__aspif.setdefault(3, []).append([len(atoms)] + atoms)

    def _output_atom(self, symbol, atom):
        """Customized for aspif output."""
        self.__symbols[atom] = symbol
        self.__aspif.setdefault(4, []).append([len(str(symbol)), str(symbol), len(atom)] + atom)

    def _output_term(self, symbol, condition):
        """Customized for aspif output."""
        self.__aspif.setdefault(4, []).append([len(str(symbol)), str(symbol), len(condition)] + condition)

    def _output_csp(self, symbol, value, condition):
        condition = sorted(set([self.__map(lit) for lit in condition]))
        self.__reified.append(Function("output_csp", [symbol, Number(value), Tuple_(condition)]))

    def _external(self, atom, value):
        """Customized for aspif output."""
        self.__aspif.setdefault(5, []).append([atom, value])

    def _assume(self, literals):
        """Customized for aspif output."""
        self.__aspif.setdefault(6, []).append([len(literals)] + list(chain.from_iterable(literals)))

    def _heuristic(self, atom, type, bias, priority, condition):
        condition = sorted(set([self.__map(lit) for lit in condition]))
        self.__reified.append(Function("heuristic", [self.__map(atom), String(str(type).replace('HeuristicType.', '')), Number(bias), Tuple_(condition)]))

    def _acyc_edge(self, node_u, node_v, condition):
        condition = sorted(set([self.__map(lit) for lit in condition]))
        self.__reified.append(Function("acyc_edge", [Number(node_u), Number(node_v), Tuple_(condition)]))

    def theory_term_number(self, term_id, number):
        self.__terms[term_id] = lambda: Number(number)

    def theory_term_string(self, term_id, name):
        self.__terms[term_id] = lambda: Function(name)

    def theory_term_compound(self, term_id, name_id_or_type, arguments):
        self.__terms[term_id] = lambda: Function(self.__terms[name_id_or_type]().name, [self.__terms[i]() for i in arguments])

    def theory_element(self, element_id, terms, condition):
        self.__elems[element_id] = lambda: Function("elem", [Tuple_([self.__terms[i]() for i in terms]), Tuple_(sorted(set([self.__map(lit) for lit in condition])))])

    def _theory_atom(self, atom_id_or_zero, term_id, elements):
        self.__symbols[atom_id_or_zero] = Function("theory", [self.__terms[term_id](), Tuple_(sorted(set([self.__elems[e]() for e in elements])))])

    def _theory_atom_with_guard(self, atom_id_or_zero, term_id, elements, operator_id, right_hand_side_id):
        self.__symbols[atom_id_or_zero] = Function("theory", [self.__terms[term_id](), Tuple_(sorted(set([self.__elems[e]() for e in elements]))), self.__terms[operator_id](), self.__terms[right_hand_side_id]()])

    def end_step(self):
        self.__reified.append(Function("end_step", []))

    def finalize(self):
        for name, args in self.__delayed:
            if name.startswith("theory_atom"):
                getattr(self, "_" + name)(*args)
        for name, args in self.__delayed:
            if not name.startswith("theory_atom"):
                getattr(self, "_" + name)(*args)
        return Context(self.__aspif)

class Context(object):

    def __init__(self, aspif):
        self.__aspif = aspif.copy()

    def get(self):
        return self.__aspif
