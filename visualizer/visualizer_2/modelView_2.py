"""
Remove unnecessary class definitions later.
"""

import parseUtils as prs
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from .configuration import *
from .model import *


class ModelScene(QGraphicsScene):
    """
    Add all elements here.
    Possibly split up into immovables and movables?
    Group items by type.
    Import whole Model at start, trigger visibility.
    """

    def __init__(self, model, config):
        super(self.__class__, self).__init__()

        self._model = model

        self._config = prs.parse_config(config)

        self._current_step = 0

    def _import_config(self, dict):
        """
        Takes a config dictionary and sets Object types and Sprites.
        Each object should have:
        - A Type
        - An Index
        - An Action (Optional)
        - A coordinate value (0ptional)
        - A Sprite / graphical representation

        Compress into (index, action) pairs per object or set individual objects with shared references?
        """
        return

    # Maybe just use model as attribute?
    def set_model(self, model):
        """
        Takes a model as defined in .model.py and adds its components to the scene.
        """
        self._model = model

    def get_step(self):
        return self._current_step

    def init_scene(self):
        """
        Sets the timestep to 0 and adjusts the model state accordingly.
        """
        self._current_step = -1
        self.next_step

    def next_step(self):
        if self._current_step >= self._model.get_states()[-1]:
            # Give back Error
            return

        self._current_step += 1
        for occ in self._model.get_states()[self._current_step]:
            self._model.get_items()[occ[0]].occur(occ[1])

    def previous_step(self):
        if self._current_step <= self._model.get_states()[0]:
            # Give back Error
            return

        for occ in self._model.get_states()[self._current_step]:
            self._model.get_items()[occ[0]].occur_reverse(occ[1])
        self._current_step -= 1


class ModelView(QGraphicsView):
    """
    Only for actual visualization of MainScene.
    """

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)
