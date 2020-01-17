from spritecontainer import SpriteContainer
from visualizeritem_2 import VisualizerItem
from visualizerabstract import VisualizerAbstract
from typing import Tuple, Dict, Iterable, Callable, Any

Obj_id = Tuple[str, int]
Occurence = Tuple[Obj_id,Tuple[Callable, Iterable[Any]]] #TODO: Specify "Any"

class Model(object):
    def __init__(self):
        self._abstracts: Dict[Obj_id, VisualizerAbstract] = None
        self._items: Dict[Obj_id, VisualizerItem] = None
        self._initial_state: Iterable[Occurence] = None
        self._occurrences: Dict[int, Iterable[Occurence]] = None
        self._sprites: SpriteContainer = None

    #TODO: Define abstract iterable
    def set_abstracts(self, abstracts):
        self._abstracts = abstracts

    def set_items(self, items: Dict[Obj_id, VisualizerItem]):
        self._items = items

    def set_initial_state(self, occ: Iterable[Occurence]):
        self._initial_state = occ
    
    def set_occurrences(self, occ: Dict[int, Iterable[Occurence]]):
        self._occurrences = occ

    def set_sprites(self, sprites: SpriteContainer):
        self._sprites = sprites

    def get_objects(self):
        return {**self._abstracts, **self._items}

    def get_abstracts(self) -> Dict[Obj_id, VisualizerAbstract]:
        return self._abstracts

    def get_items(self) -> Dict[Obj_id, VisualizerItem]:
        return self._items

    def get_initial_state(self) -> Iterable[Occurence]:
        return self._initial_state

    def get_occurrences(self) -> Dict[int, Iterable[Occurence]]:
        return self._occurrences

    def get_sprites(self) -> SpriteContainer:
        return self._sprites