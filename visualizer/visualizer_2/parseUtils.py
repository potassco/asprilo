import sys
import clingo
from visualizerItem_2 import *
import yaml
import logging
from model_2 import *


def validate_atom(atom, cfg):
    """
    Pattern matching to validate atom structure against config? RE maybe?
    """
    return

#TODO: Rewrite, Add configurability (maybe recursively)
def parse_init_atom(symbols, cfg):
    if len(symbols) != 2:
        #TODO: Error
        return

    for symbol in symbols:

        if symbol.name == "object":
            obj_id = (symbol.arguments[0].name, symbol.arguments[1].number)

        elif symbol.name == "value":
            coord = tuple(x.number for x in symbol.arguments[1].arguments)

        else:
            #TODO: Error
            pass
        
    occur = (obj_id, ("init", coord))
    item = VisualizerItem(obj_id, cfg["object"][obj_id[0]])

    return obj_id, item, occur


#TODO: Rewrite, Add configurability
def parse_occurs_atom(symbols, cfg):
    if len(symbols) != 3:
        #TODO: Error
        return

    index = symbols[2].number
    obj_id = (symbols[0].arguments[0].name, symbols[0].arguments[1].number)
    action = (symbols[1].arguments[0].name, tuple(x.number for x in symbols[1].arguments[1].arguments))
        
    return index, (obj_id, action)

def parse_clingo_model(cl_handle, atomcfg, compress_lists=False):
    """
    Parse a gringo model as returned by clingo and return an equivalent
    visualizer model.
    """
    model = Model()
    itemdict = {}
    init = []
    occurs = {}

    for cl_model in cl_handle:
        for symbol in cl_model.symbols(atoms=True):
                    
            if symbol.name == "occurs":
                # Parse atom, append to states
                index, occur = parse_occurs_atom(symbol.arguments, atomcfg)
                occurs.setdefault(index, []).append(occur)

            elif symbol.name == "init":
                #Skip some atoms for now
                #TODO: Remove workaround, implement case properly
                if symbol.arguments[0].arguments[0].name == "order":
                    pass

                else:
                    # Parse atom, append to items/states
                    obj_id, item, occur = parse_init_atom(symbol.arguments, atomcfg)
                    itemdict[obj_id] = item
                    init.append(occur)

            else:
                #TODO: Throw error "unknown atom type(occurs)"
                pass

    model.set_items(itemdict)

    if compress_lists:
        init = (action for action in init)
        for occ in occurs:
            occurs[occ] = (action for action in occurs[occ])
    model.set_initial_state(init)
    model.set_occurrences(occurs)

    return model

def parse_config(yml):
    """
    Attempts to read parameters from a YAML file and uses defaults when given None.
    """
    
    if yml is None:
        # Implement default case
        sys.exit("no config file found")

    else:
        with yml as stream:
            try:
                cfg_dict = yaml.safe_load(stream)
            except yaml.YAMLError as exception:
                logging.error(exception)
                sys.exit("Error while parsing config file")

    return cfg_dict