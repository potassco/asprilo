import sys
import clingo
from visualizerItem_2 import *
import yaml
import logging
import typing
from typing import Dict
from model_2 import *


def parse_spritepath(path):
    return #Reference to sprite file

def parse_value(symbols, itemcfg):
    return

def parse_object(name: str, number: int, itemcfg: Dict[str,str], spriteconfig):
    objtype = itemcfg[name]
    obj_id = (name, number)

    if objtype == "static" or objtype == "movable":
        item = VisualizerItem(obj_id, spriteconfig[name])

    elif objtype == "abstract":
        item = VisualizerAbstract(obj_id)

    return objtype, obj_id, item

#TODO: Rewrite, Add configurability (maybe recursively)
# Split for movables, abstracts and statics
def parse_init_atom(symbols, itemcfg, spriteconfig):
    if len(symbols) != 2:
        #TODO: Error
        return

    for symbol in symbols:

        if symbol.name == "object":
            objtype, obj_id, item = parse_object(symbol.arguments[0].name, symbol.arguments[1].number, itemcfg, spriteconfig)

        elif symbol.name == "value":
            coord = tuple(x.number for x in symbol.arguments[1].arguments)

        else:
            #TODO: Error
            pass
        
    occur = (obj_id, ("init", coord))

    return objtype, obj_id, item, occur


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
    
    objects = {"movable": {}, "static": [], "abstract": {}}
    init = []
    occurs = {}

    # Dictionary of the form obj_id: objtype
    itemcfg = dict(((obj, att[0]) for att in atomcfg["object"].items() for obj in att[1]))

    # Dictionary of the form obj_id: sprite
    spritecfg = dict((obj, parse_spritepath(att[obj])) for att in atomcfg["object"].values() for obj in att)

    for cl_model in cl_handle:
        for symbol in cl_model.symbols(atoms=True):
                    
            if symbol.name == "occurs":
                # Parse atom, append to states
                index, occur = parse_occurs_atom(symbol.arguments, itemcfg)
                occurs.setdefault(index, []).append(occur)

            elif symbol.name == "init":
                #Skip some atoms for now
                #TODO: Remove workaround, implement case properly
                if itemcfg[symbol.arguments[0].arguments[0].name] == "abstract":
                    pass

                else:
                    # Parse atom, append to items/states
                    objtype, obj_id, item, occur = parse_init_atom(symbol.arguments, itemcfg, spritecfg)
                    if objtype == "static":
                        #objects["static"].append(item) # TODO:  remove Workaround, currently bugged
                        objects["movable"][obj_id] = item
                    else:
                        objects[objtype][obj_id] = item 

                    init.append(occur)
            else:
                #TODO: Throw error "unknown atom type(occurs)"
                pass
    
    if compress_lists:
        init = (action for action in init)
        for occ in occurs:
            occurs[occ] = (action for action in occurs[occ])

    model = Model()
    model.set_items(objects["movable"])
    model.set_statics(objects["static"])
    model.set_abstracts(objects["abstract"])
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
