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

def parse_clingo_model(cl_model, config):
    """
    Parse a gringo model as returned by clingo and return an equivalent
    visualizer model.
    """
    model = Model()
    itemdict = {}
    statelist = []






    model.set_items(itemdict)
    model.set_states(statelist)
    return model
    