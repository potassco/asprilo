from visualizerItem_2 import *



class Model(object):
    def __init__(self):
        self._items = None
        self._initial_state = None
        self._occurrences = None

    def set_items(self, itemdict):
        """
        Expected:
        - dict {(<type>, Index): visualizerItem}
        """
        self._items = itemdict

    def set_initial_state(self, actiondict):
        """
        Expected:
        - dict {(<type>, Index): visualizerItem}
        """
        self._initial_state = actiondict
    
    def set_occurrences(self, actiondict):
        """
        Expected:
        - List of generators of tuples ((<type>, Index), (Action,argument))
        """
        self._occurrences = actiondict

    def get_items(self):
        return self._items

    def get_initial_state(self):
        """
        Expected:
        - dict {(<type>, Index): visualizerItem}
        """
        return self._initial_state

    def get_occurrences(self):
        return self._occurrences