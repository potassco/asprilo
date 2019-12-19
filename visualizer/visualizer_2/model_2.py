from visualizerItem_2 import VisualizerItem
from visualizerAbstract import VisualizerAbstract
from typing import Tuple, Dict, Iterable, Callable, Any

Obj_id = Tuple[str, int]
Action = Tuple[Obj_id,Tuple[Callable, Iterable[Any]]] #TODO: Specify "Any"

class Model(object):
    def __init__(self):
        self._abstracts: Dict[Obj_id, VisualizerAbstract] = None
        self._statics: Iterable[VisualizerItem] = None
        self._items: Dict[Obj_id, VisualizerItem] = None
        self._initial_state: Iterable[Action] = None
        self._occurrences: Dict[int, Iterable[Action]] = None

    #TODO: Define abstract iterable
    def set_abstracts(self, abstracts):
        self._abstracts = abstracts

    def set_statics(self, statics: Iterable[VisualizerItem]):
        self._statics = statics

    def set_items(self, items: Dict[Obj_id, VisualizerItem]):
        self._items = items

    def set_initial_state(self, actions: Iterable[Action]):
        self._initial_state = actions
    
    def set_occurrences(self, actions: Dict[int, Iterable[Action]]):
        self._occurrences = actions
    
    def get_abstracts(self) -> Dict[Obj_id, VisualizerAbstract]:
        return self._abstracts

    def get_statics(self) -> Iterable[VisualizerItem]:
        return self._statics

    def get_items(self) -> Dict[Obj_id, VisualizerItem]:
        return self._items

    def get_initial_state(self) -> Iterable[Action]:
        return self._initial_state

    def get_occurrences(self) -> Dict[int, Iterable[Action]]:
        return self._occurrences