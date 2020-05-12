"""
Remove unnecessary class definitions later.
"""

import time
import parseutils as prs
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QOpenGLWidget
from PyQt5.QtGui import *
from model import *


class ModelScene(QGraphicsScene):
    """
    Add all elements here.
    Possibly split up into immovables and movables?
    Group items by type.
    Import whole Model at start, trigger visibility.
    """

    currentStepChanged = pyqtSignal(int)

    def __init__(self, model):
        super().__init__()
        
        self._model = model
        self._current_step = 0
        self._paths_visible = True

        self._animate_movements = False
        self._steptime = 400  # ms
        self._framerate = 5  # Hz
        
        self._import_items()
        # self.init_scene()
        self.setSceneRect(self.sceneRect())

    def set_model(self, model):
        """
        Removes all elements from the scene (deletes all items!).
        Takes a model as defined in .model.py and adds its components to the scene.
        """
        self.clear()
        self._model = model
        self._current_step = 0
        self.import_items()
        # self.init_scene()

    def get_step(self):
        return self._current_step

    def get_sprites(self):
        return self._model.get_sprites()

    def _import_items(self):
        for item in self._model.get_items().values():
            self.addItem(item)
        for path in self._model.get_paths().values():
            self.addItem(path)

    def reset_scene(self, *, signal=True):
        """
        Sets the timestep to 0 and adjusts the model state accordingly.
        """
        print("Setting Scene to t = 0")
        for item in self._model.get_items().values():
            item.reset_to_start()
        for abstract in self._model.get_abstracts().values():
            abstract.reset_to_start()
        self._current_step = 0
        if signal:
            self.currentStepChanged.emit(self._current_step)

    def next_step(self, *, signal=True):
        """
        Increases the scene's timestep by 1.
        """

        if self._current_step >= len(self._model.get_occurrences()):
            # Give back Error
            print(f"Step {self._current_step} is the last one in the model!")
            return

        print("Next step: " + str(self._current_step + 1))
        self._current_step += 1

        if self._animate_movements:
            steps = self._steptime * self._framerate // 1000
            wait = self._steptime / (steps * 1000)
            print(steps)
            print(wait)
            occurrences = self._model.get_occurrences().get(self._current_step, [])
            # First include all actions
            for occ in occurrences:
                    if occ[1][0] is actions.move:
                        occ[1][0](self._model.get_items()[occ[0]],
                                  occ[1][1][0]/steps, occ[1][1][1]/steps)
                    else:
                        occ[1][0](self._model.get_items()[occ[0]], *occ[1][1])
            time.sleep(wait)
            
            #Then for the following steps only moves
            for t in range(steps-1):
                for occ in occurrences:
                    if occ[1][0] is actions.move:
                        occ[1][0](self._model.get_items()[occ[0]],
                                  occ[1][1][0]/steps, occ[1][1][1]/steps)
                        self._model.get_items()[occ[0]].repaint()
                        time.sleep(wait)

        else:
            for occ in self._model.get_occurrences().get(self._current_step, []):
                occ[1][0](self._model.get_items()[occ[0]], *occ[1][1])

        print(signal)
        if signal:
            self.currentStepChanged.emit(self._current_step)

    def previous_step(self, *, signal=True):
        """
        Decreases the scene's timestep by 1.
        """

        if self._current_step < 1:
            # Give back Error
            print(f"Step {self._current_step} is the first one in the model!")
            return

        print("Previous Step:" + str(self._current_step - 1))
        if self._animate_movements:
            steps = self._steptime * self._framerate // 1000
            wait = self._steptime // (steps * 1000)
            print(steps)
            print(wait)
            occurrences = self._model.get_occurrences().get(self._current_step, [])
            # First include all actions
            for occ in occurrences:
                    if occ[1][0] is actions.move:
                        occ[1][0].rev(self._model.get_items()[occ[0]],
                                  occ[1][1][0]/steps, occ[1][1][1]/steps)
                    else:
                        occ[1][0].rev(self._model.get_items()[occ[0]], *occ[1][1])
            time.sleep(wait)
            
            #Then for the following steps only moves
            for t in range(steps-1):
                for occ in occurrences:
                    if occ[1][0] is actions.move:
                        occ[1][0].rev(self._model.get_items()[occ[0]],
                                  occ[1][1][0]/steps, occ[1][1][1]/steps)
                        time.sleep(wait)

        else:
            for occ in self._model.get_occurrences().get(self._current_step, []):
                occ[1][0].rev(self._model.get_items()[occ[0]], *occ[1][1])
        
        self._current_step -= 1
        if signal:
            self.currentStepChanged.emit(self._current_step)
 
    def last_step(self, *, signal=True):
        self.go_to_step(max(self._model.get_occurrences()),signal=signal)

    def go_to_step(self, step, signal=True):
        diff = self._current_step - int(step)

        if diff < 0:  # go forwards
            for x in range(-diff):
                self.next_step(signal=False)

        elif diff > 0:  # go backwards
            for x in range(diff):
                self.previous_step(signal=False)

        if signal:
            self.currentStepChanged.emit(self._current_step)

    def toggle_paths(self):
        for path in self._model.get_paths().values():
            path.setVisible(not self._paths_visible)
        self._paths_visible = not self._paths_visible

    def set_animation(self, boolean):
        self._animate_movements = boolean

    def save_to_png(self):
        # Create image with the exact size of the shrunk scene
        image = QImage(1920, 1080, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        self.render(QPainter(image))
        image.save("Visualizer_Scene.png")

