
from PyQt5.QtCore import QRectF, QRect
from PyQt5.QtWidgets import QGraphicsItem


class VisualizerItem(QGraphicsItem):

    def __init__(self, obj_id, startcoord, spritecontainer, zvalue):
        super().__init__()
        self._name, self._id = obj_id[0], obj_id[1]
        self._startcoord = startcoord
        self._spritecontainer = spritecontainer
        self._spritekey = spritecontainer.get_keys()[self._name]
        self._path = None
        self._mark = None
        self._held_items = []
        self.reset_to_start()
        self.setZValue(zvalue)
        self.setToolTip(f"{self._name} {self._id}")
        self.update()

    def get_name(self):
        return self._name
    
    def get_id(self):
        return self._id

    def get_obj_id(self):
        return (self._name, self._id)

    def boundingRect(cls):
        return QRectF(0, 0, 1, 1)

    def paint(self, painter, option, widget):
        painter.drawPixmap(QRect(0, 0, 1, 1),
                           self._spritecontainer.find(self._spritekey))
    
    def set_path(self, path):
        path.set_start(self._startcoord)
        path.setZValue(self.zValue()-1)
        self._path = path
        
    def get_path(self):
        return self._path

    def holds_item(self, obj):
        return obj in self._held_items

    def get_held_items(self):
        return self._held_items
    
    def pick_up(self, obj):
        if not self.holds_item(obj):
            self._held_items.append(obj)
            if not self._mark.isVisible():
                self._set_mark_visibility(True)

    def put_down(self, obj):
        if self.holds_item(obj):
            self._held_items.remove(obj)
            if not self._held_items:
                self._set_mark_visibility(False)

    def _set_path_visibility(self, visible):
        if self._path is not None:
            self._path.setVisible(visible)

    def _set_mark_visibility(self, visible):
        if self._mark is None:
            self._mark = VisualizerItemMark(self._spritecontainer, self)
        self._mark.setVisible(visible)

    def reset_to_start(self):
        for item in self._held_items:
            self.put_down(item)
        self._set_mark_visibility(False)
        self.setPos(*self._startcoord)


class VisualizerItemMark(QGraphicsItem):
    def __init__(self, spritecontainer, parent):
        super().__init__(parent=parent)
        self._spritecontainer = spritecontainer
        self._spritekey = spritecontainer.get_keys()["mark"]
        self.setZValue(float("inf"))
    
    def get_name(self):
        return None
    
    def get_id(self):
        return None

    def get_obj_id(self):
        return (None, None)

    def boundingRect(cls):
        return QRectF(0, 0, 1, 1)
        
    def paint(self, painter, option, widget):
        painter.drawPixmap(QRect(0, 0, 1, 1),
                           self._spritecontainer.find(self._spritekey))
    
    def remove(self):
        self.setParentItem(None)


class VisualizerItemPath(QGraphicsItem):

    def __init__(self):
        super().__init__()
        self._start = QPoint(0,0)
        self._path = QPainterPath()
    
    def get_name(self):
        return None
    
    def get_id(self):
        return None

    def get_obj_id(self):
        return (None, None)

    def set_start(self, coord):
        self._start = coord

    def add_step(self, direction):
        self._path.append(direction)
    
    def paint(self, painter, option, widget):
        painter.drawPath(self._path)

