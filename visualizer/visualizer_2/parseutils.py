import sys
import clingo
import visualizeritem_2
from spritecontainer import SpriteContainer
from PyQt5.QtSvg import QSvgRenderer
import yaml
import logging
import typing
import actions
from typing import Dict
from model_2 import *


def parse_action(action: str, args: list, actioncfg: Dict[str, str], pickuplist):

    ignore = ("dummy", "demand", "satisfy")  # WIP functions
    if actioncfg[action] in ignore:
        return actions.dummy, ()

    if actioncfg[action] == "move":
        arglist = [x.number for x in args]
        return actions.move, tuple(arglist)

    if actioncfg[action] == "pick_up":
        arglist = [(x.name, x.number) for x in args]
        return actions.pick_up, tuple(arglist)

    if actioncfg[action] == "pick_up_all":
        # arglist = [x.number for x in args]
        # arglist.append(pickuplist)
        return actions.pick_up_all, [pickuplist]

    if actioncfg[action] == "put_down":
        arglist = [(x.name, x.number) for x in args]
        return actions.put_down, tuple(arglist)

    if actioncfg[action] == "put_down_all":
        # arglist = [x.number for x in args]
        # arglist.append(pickuplist)
        return actions.put_down_all, [pickuplist]

    if actioncfg[action] == "demand":
        return actions.demand

    if actioncfg[action] == "satisfy":
        return actions.satisfy

def parse_item(name: str, number: int, initargs, itemcfg: Dict[str, str], sprites, zvalues):

    coord = tuple(x.number for x in initargs[1].arguments)
    item = VisualizerItem((name, number), coord, sprites, zvalues[name])

    return item


def parse_abstract(name: str, number: int, initargs, itemcfg: Dict[str, str]):
    abstract = VisualizerAbstract((name, number))

    # TODO: Implement classification for orders/products
    #action = (actions.dummy, tuple(initargs))

    return abstract


def parse_init_atom(symbols, itemcfg, sprites, zvalues):
    if len(symbols) != 2:
        #TODO: Error
        return

    name = symbols[0].arguments[0].name
    number = symbols[0].arguments[1].number
    initargs = symbols[1].arguments
    objtype = itemcfg[name]
    obj_id = (name, number)

    if objtype == "item":
        obj = parse_item(
            name, number, initargs, itemcfg, sprites, zvalues)

    elif objtype == "abstract":
        obj = parse_abstract(name, number, initargs, itemcfg)

    else:
        pass  # TODO: Error

    return objtype, obj_id, obj


# TODO: Rewrite, Add configurability
def parse_occurs_atom(symbols, actioncfg, pickuplist):
    if len(symbols) != 3:
        #TODO: Error
        return

    index = symbols[2].number
    obj_id = (symbols[0].arguments[0].name, symbols[0].arguments[1].number)
    occargs = symbols[1].arguments
    action = (parse_action(symbols[1].arguments[0].name,
                           occargs[1].arguments, actioncfg, pickuplist))

    return index, (obj_id, action)


def parse_clingo_model(cl_handle, atomcfg):
    """
    Parse a gringo model as returned by clingo and return an equivalent
    visualizer model.
    """
    print("Converting to VisualizerModel...")

    objects = {"item": {}, "abstract": {}}
    #init = []
    occurs = {}
    atoms = {}

    # Dictionary of the form objname: objtype
    itemcfg = {obj: att[0] for att in atomcfg["object"].items()
               for obj in att[1]}

    sprites = SpriteContainer(atomcfg["object"]["item"])
    zvalues = {name: 2*atomcfg["layer"].index(name)
               for name in atomcfg["layer"]}

    for cl_model in cl_handle:
        for symbol in cl_model.symbols(atoms=True):

            if symbol.name == "occurs":
                # Parse atom, append to states
                index, occur = parse_occurs_atom(
                    symbol.arguments, atomcfg["action"], atomcfg.get("portable", []))
                occurs.setdefault(index, []).append(occur)

                # Keep string representation of atom in separate dict
                atoms.setdefault(index, []).append(str(symbol))

            elif symbol.name == "init":
                # Parse atom, append to items/states
                objtype, obj_id, obj = parse_init_atom(
                    symbol.arguments, itemcfg, sprites, zvalues)
                objects[objtype][obj_id] = obj
                
                # Keep string representation of atom in separate dict
                atoms.setdefault(0, []).append(str(symbol))

            else:
                # TODO: Throw error "unknown atom type(occurs)"
                pass
        break

    
    model = Model()
    model.set_items(objects["item"])
    model.set_abstracts(objects["abstract"])
    #model.set_initial_state(init)
    model.set_occurrences(occurs)
    model.set_sprites(sprites)

    for alist in atoms.values():
        alist.sort()
    model.set_atoms(atoms)

    model.calculate_item_paths()
    model.set_colorcoding(atomcfg.get("colorcode", []))
    
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
