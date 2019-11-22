from .visualizerItem import *
from .visualizerGraphicItem import *


class Model(object):
    def __init__(self):
        self._items = None
        self._states = None

    def set_items(self, itemdict):
        """
        Expected:
        - dict {(<type>, Index): visualizerItem}
        """
        self._items = itemdict
    
    def set_states(self, statedict):
        """
        Expected:
        - List of generators of tuples ((<type>, Index), Action)
        """
        self._states = statedict

    def get_items(self):
        return self._items

    def get_states(self):
        return self._states