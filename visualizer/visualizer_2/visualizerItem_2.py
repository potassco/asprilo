
from PyQt5.QtCore import *
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtGui import QBrush


class VisualizerItem(QGraphicsSvgItem):

    def __init__(self, obj_id, renderer):
        super().__init__()
        self._obj_id = obj_id
        self.setSharedRenderer(renderer)
        self.setToolTip(str(self._obj_id))
    #    self._init_brush()
#        self._sprite = sprite
        self.update()

    def get_obj_id(self):
        return self._obj_id

#    def get_sprite(self):
#        self.paint()
#        return self._sprite

    def _init_brush(self):
        if self._obj_id[0] == "node":
            self._brush = QBrush(Qt.darkGray)
        elif self._obj_id[0] == "highway":
            self._brush = QBrush(Qt.lightGray)
        elif self._obj_id[0] == "robot":
            self.setZValue(1)
            self._brush = QBrush(Qt.magenta)
        elif self._obj_id[0] == "shelf":
            self._brush = QBrush(Qt.blue)
        elif self._obj_id == "pickingStation":
            self._brush = QBrush(Qt.yellow)
        else:
            self._brush = QBrush(Qt.green)


    def boundingRect(self):
        return QRectF(0,0,4,5.5)

    def paint(self, painter, option, widget):
            #print("Painting atom:" + self._obj_id[0])
            #painter.fillRect(self.boundingRect(), self._brush)
            self.renderer().render(painter, self.boundingRect())
            return

    # def occur(self, action):
    #     if action[0] == "init":
    #         self.setPos(action[1][0]*50, action[1][1]*50)

    #     elif action[0] == "move":
    #         self.moveBy(action[1][0]*50, action[1][1]*50)

    #     else:
    #         # Give Warning f"Unhandled action {action[0]} at timestep t"
    #         return
        
    #    # self.update()

    # def occur_reverse(self, action):
    #     if action[0] == "move":
    #         self.moveBy(- action[1][0]*50, - action[1][1]*50)

    #     else:
    #         # Give Warning f"Unhandled action {action[0]} (reverse) at timestep t"
    #         return
        
    #    # self.update()
