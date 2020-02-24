
from PyQt5.QtCore import QRectF, QRect
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QTransform


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

    def get_startcoord(self):
        return self._startcoord

    def boundingRect(cls):
        return QRectF(0, 0, 1, 1)

    def paint(self, painter, option, widget):
        painter.drawPixmap(QRect(0, 0, 1, 1),
                           self._spritecontainer.find(self._spritekey))

    def set_path(self, movelist):
        self._path = VisualizerItemPath(
            self._startcoord, movelist, self._spritecontainer)
        self._path.setZValue(self.zValue()-1)
        self.scene().addItem(self._path)

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
        self._spritekey = spritecontainer.get_keys()["$mrk"]
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

    def __init__(self, parent_id, start, movelist, spritecontainer):
        super().__init__()
        self._parent_id = parent_id
        self._start = start
        self._spritecontainer = spritecontainer
        self._rotations = (QTransform().rotate(0),
                           QTransform().rotate(90),
                           QTransform().rotate(180),
                           QTransform().rotate(270))
        self._path = self.compute_path(movelist)
        self._spritekeys = tuple(spritecontainer.get_keys()[k] for k in [
                                 "$p1b", "$p2s", "$p2c", "$p4e"])
        self.setFlag(self.ItemIgnoresParentOpacity)
        self.setOpacity(0.3)

    def boundingRect(cls):
        return QRectF(0, 0, 1, 1)

    def paint(self, painter, option, widget):
        for step in self._path:
            painter.drawPixmap(QRect(*step[0], 1, 1), self._spritecontainer.find(
                self._spritekeys[step[1][0]]).transformed(self._rotations[step[1][1]]))

    # TODO: centralize dirs
    def compute_path(self, moves):
        # Cardinal directions in clockwise order, starting at up
        dirs = {(0, -1): 0, (1, 0): 1, (0, 1): 2, (-1, 0): 3}
    
        # Initialize path with start segment
        x, y = self._start[0], self._start[1]
        path = [((x, y), (0, (dirs[moves[0][1]] + 2) % 4)), ]
        x, y = x + moves[0][1][0], y + moves[0][1][1]

        # Append other segments
        for index in range(1, len(moves)):
            path.append(((x, y), (self._get_tile(moves[index-1][1], moves[index][1], dirs))))
            x, y = x + moves[index][1][0], y + moves[index][1][1]

        # End with end segment
        path.append(((x, y), (3, dirs[moves[-1][1]])))

        return tuple(path)

    def _get_tile(self, enter, leave, dirs):

        print(f"{(enter, leave)}")
        # Compute angle of turn on tile
        turn = (dirs[enter] - dirs[leave]) % 4
        # Straight / no turn
        if turn == 0:
            tile = 1
            orientation = dirs[enter]
        # Turn right
        elif turn == 3:
            tile = 2
            orientation = dirs[enter]
        # Turn back
        elif turn == 2:
            tile = 0
            orientation = dirs[enter]
        # Turn left
        elif turn == 1:
            tile = 2
            orientation = (dirs[enter] + 1) % 4

        else:
            print("Error while creating path")
            return (0,0)

        return (tile, orientation)

    def get_name(self):
        return None

    def get_id(self):
        return None

    def get_obj_id(self):
        return (None, None)

    def get_parent_id(self):
        return self._parent_id

    def set_start(self, coord):
        self._start = coord

    def add_step(self, direction):
        self._path.append(direction)
