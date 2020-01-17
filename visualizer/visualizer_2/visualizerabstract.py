
# from PyQt5.QtCore import *
# from PyQt5.QtWidgets import QGraphicsItem
# from PyQt5.QtGui import QBrush

#TODO: Symbolizes abstract constraint, can be satisfied
class VisualizerAbstract:

    def __init__(self, obj_id):
        #super().__init__()
        self._obj_id = obj_id
        
    def get_obj_id(self):
        return self._obj_id
