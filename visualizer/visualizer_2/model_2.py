from spritecontainer import SpriteContainer
from visualizeritem_2 import *
from visualizerabstract import VisualizerAbstract
from typing import Tuple, Dict, Iterable, Callable, Any
import actions
from PyQt5.QtGui import QColor

Obj_id = Tuple[str, int]
# TODO: Specify "Any"
Occurence = Tuple[Obj_id, Tuple[Callable, Iterable[Any]]]


class Model(object):
    def __init__(self):
        self._abstracts: Dict[Obj_id, VisualizerAbstract] = None
        self._items: Dict[Obj_id, VisualizerItem] = None
        self._occurrences: Dict[int, Iterable[Occurence]] = None
        self._paths: Dict[Obj_id, VisualizerItemPath] = None
        self._sprites: SpriteContainer = None
        self._atoms: Dict[int, Iterable[str]] = None

    # TODO: Define abstract iterable
    def set_abstracts(self, abstracts):
        self._abstracts = abstracts

    def set_items(self, items: Dict[Obj_id, VisualizerItem]):
        self._items = items

    def set_occurrences(self, occ: Dict[int, Iterable[Occurence]]):
        self._occurrences = occ

    def set_sprites(self, sprites: SpriteContainer):
        self._sprites = sprites

    def set_atoms(self, atoms: Dict[int, Iterable[str]]):
        self._atoms = atoms

    def get_objects(self):
        return {**self._abstracts, **self._items}

    def get_abstracts(self) -> Dict[Obj_id, VisualizerAbstract]:
        return self._abstracts

    def get_items(self) -> Dict[Obj_id, VisualizerItem]:
        return self._items

    def get_occurrences(self) -> Dict[int, Iterable[Occurence]]:
        return self._occurrences
    
    def get_paths(self) -> Dict[Obj_id, VisualizerItemPath]:
        return self._paths

    def get_sprites(self) -> SpriteContainer:
        return self._sprites
    
    def get_atoms(self) -> Dict[int, Iterable[str]]:
        return self._atoms

    # TODO: Probably has room for optimization
    def calculate_item_paths(self):
        print("Calculating Paths...")
        temp_paths = {}
        for key in sorted(self._occurrences):
            for occ in self._occurrences[key]:
                if occ[1][0] is actions.move:
                    temp_paths.setdefault(occ[0], []).append(occ[1])

        paths = {}
        for path in temp_paths.items():
            item = self._items[path[0]]  # .set_path(path[1])
            itempath = VisualizerItemPath(
                path[0], item.get_startcoord(), path[1], self._sprites)
            itempath.setZValue(item.zValue()-1)
            paths[path[0]] = itempath
        
        self._paths = paths

    def set_colorcoding(self, colorlist):
        amounts = {}
        for name in colorlist:
            amounts[name] = max(1, sum(x[0] == name for x in self._items))
        for item in self._items.items():
            if item[0][0] in colorlist:
                effect = QGraphicsColorizeEffect()
                effect.setColor(QColor.fromHsl(max(0,item[0][1]-1) * 256/max(1,amounts[item[0][0]]-1), 255, 128, 255))
                item[1].setGraphicsEffect(effect)

        for item in self._paths.items():
            if item[0][0] in colorlist:
                effect = QGraphicsColorizeEffect()
                effect.setColor(QColor.fromHsl(max(0,item[0][1]-1) * 256/max(1,amounts[item[0][0]]-1), 255, 128, 255))
                item[1].setGraphicsEffect(effect)
