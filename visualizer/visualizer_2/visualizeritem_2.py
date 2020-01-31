
from PyQt5.QtCore import QRectF, QRect
from PyQt5.QtWidgets import QGraphicsItem

class VisualizerItem(QGraphicsItem):

    def __init__(self, obj_id, spritecontainer, zvalue):
        super().__init__()
        self._name, self._id = obj_id[0], obj_id[1]
        #self.setPixmap(pixmap)
        self._spritecontainer = spritecontainer
        self._key = spritecontainer.get_keys()[self._name]
        self.setZValue(zvalue)
        self.setToolTip(f"{self._name} {self._id}")
        self.update()

    def boundingRect(cls):
        return QRectF(0,0,1,1)

#    def get_sprite(self):
#        self.paint()
#        return self._sprite

    # def _init_brush(self):
    #     if self._obj_id[0] == "node":
    #         self._brush = QBrush(Qt.darkGray)
    #     elif self._obj_id[0] == "highway":
    #         self._brush = QBrush(Qt.lightGray)
    #     elif self._obj_id[0] == "robot":
    #         self.setZValue(1)
    #         self._brush = QBrush(Qt.magenta)
    #     elif self._obj_id[0] == "shelf":
    #         self._brush = QBrush(Qt.blue)
    #     elif self._obj_id == "pickingStation":
    #         self._brush = QBrush(Qt.yellow)
    #     else:
    #         self._brush = QBrush(Qt.green)

    def paint(self, painter, option, widget):
            painter.drawPixmap(QRect(0,0,1,1), self._spritecontainer.find(self._key))


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
