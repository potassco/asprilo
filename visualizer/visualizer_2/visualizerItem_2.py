
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsItem

class VisualizerItem(QGraphicsItem):
    
    def __init__(self, obj_id, sprite):
        self._obj_id = obj_id
        self._sprite = sprite
        self.sync_pos()
        
    def get_obj_id(self):
        return self._obj_id
    
    def get_sprite(self):
        return self._sprite

    def occur(self, action):
        if action[0] == "init":
            self.setPos(action[1][0], action[1[1]])

        elif action[0] == "move":
            self.moveBy(action[1][0], action[1[1]])
        
        else:
            # Give Warning f"Unhandled action {action[0]} at timestep t"
            return

    def occur_reverse(self, action):
        if action[0] == "move":
            self.moveBy(- action[1][0], - action[1[1]])

        else:
            # Give Warning f"Unhandled action {action[0]} (reverse) at timestep t"