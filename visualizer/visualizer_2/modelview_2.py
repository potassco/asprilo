"""
Remove unnecessary class definitions later.
"""

import parseutils as prs
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QOpenGLWidget
from PyQt5.QtGui import *
from model_2 import *


class ModelScene(QGraphicsScene):
    """
    Add all elements here.
    Possibly split up into immovables and movables?
    Group items by type.
    Import whole Model at start, trigger visibility.
    """

    def __init__(self, model):
        super().__init__()

        self._model = model
        self._current_step = -1
        self._import_items()
        self.init_scene()

    def set_model(self, model):
        """
        Removes all elements from the scene (deletes all items!).
        Takes a model as defined in .model.py and adds its components to the scene.
        """
        self.clear()
        self._model = model
        self.import_items()
        self.init_scene()

    def get_step(self):
        return self._current_step

    def _import_items(self):
        for item in list(self._model.get_items().values()):
            self.addItem(item)
            #print(item.renderer())

    def init_scene(self):
        """
        Sets the timestep to 0 and adjusts the model state accordingly.
        """
        print("Setting Scene to t = 0")
        objects = self._model.get_objects()

        # Check actions and call used functions
        for init in self._model.get_initial_state():
            init[1][0](objects[init[0]], *init[1][1])
        
        self._current_step = 0

    # def _group_statics(self):
    #     print("Grouping static objects...")
    #     self.createItemGroup(self._model.get_statics().values())

    # def reset_scene(self):
    #     """
    #     Sets the timestep to 0 and adjusts the model state accordingly.
    #     """
    #     print("Setting Scene to t = 0")
    #     if self._current_step == 0:
    #         return
    #     for init in self._model.get_initial_state():
    #         self._model.get_items()[init[0]].occur(init[1])
    #     self._current_step = 0

    def next_step(self):
        print("Next step: " + str(self._current_step + 1))
        # Maybe in try/catch?
        if self._current_step >= len(self._model.get_occurrences()):
            print(f"Step {self._current_step} is the last one in the model!") #Give back Error
            return

        self._current_step += 1
        for occ in self._model.get_occurrences()[self._current_step]:
            occ[1][0](self._model.get_items()[occ[0]], *occ[1][1])

    def previous_step(self):
        print("Previous Step:" + str(self._current_step - 1))
        if self._current_step <= 0:
            print(f"Step {self._current_step} is the first one in the model!") #Give back Error
            return

        for occ in self._model.get_occurrences()[self._current_step]:
            occ[1][0].rev(self._model.get_items()[occ[0]], *occ[1][1])
        self._current_step -= 1


class ModelView(QGraphicsView):
    """
    Only for actual visualization of MainScene.
    """

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)
        self._scene = scene
        self.setViewport(QOpenGLWidget())
    
    def resizeToFit(self):
        print("Resizing Window...")
        self.fitInView(self._scene.sceneRect())

    def get_scene(self):
        return self._scene