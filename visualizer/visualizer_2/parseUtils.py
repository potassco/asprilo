import os.path
import clingo
from . import configuration
import traceback
from .model_2 import *


def validate_atom(atom, config):
    """
    Pattern matching to validate atom structure against config? RE maybe?
    """
    return

def parse_init_atom(atom, config):
    return obj_id, atom_

def parse_occurs_atom(atom, config):
    return atom_

def parse_clingo_model(cl_model, config):
    """
    Parse a gringo model as returned by clingo and return an equivalent
    visualizer model.
    """
    model = Model()
    itemdict = {}
    statedict = {}

    for symbol in cl_model.symbols(atoms=True):
        
        validate_atom(symbol, config)
        
        if symbol.name == "occurs":
            # Parse atom, append to states
            atom = symbol.arguments

            return

        elif symbol.name == "init":
            # Parse atom, append to items/states
            return
            


    model.set_items(itemdict)

    for state in statedict:
        state = (x for x in state)
    model.set_states(statedict)

    return model
    