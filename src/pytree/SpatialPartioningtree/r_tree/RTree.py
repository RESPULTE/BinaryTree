from typing import Dict, List

from ..utils import BBox
from ..type_hints import UID

from ._r_node import R_Entity, R_Node


class RTree:

    def __init__(self, node_capacity: int = 4) -> None:
        self.node_capacity = node_capacity

        # for caching
        self._free_r_node = None
        self._free_r_entity = None

        self.all_r_node: List[R_Node] = []
        self.all_r_entity: Dict[UID, R_Entity] = {}

    def insert(self, entity_id: UID, entity_bbox: BBox) -> None:
        pass

    def delete(self, entity_id: UID) -> None:
        pass

    def pop(self, entity_id: UID) -> None:
        pass

    def clear(self, rm_cached: bool = False) -> None:
        pass

    def clean_up(self) -> None:
        pass

    def query(self) -> List[UID]:
        pass

    def split_rnode(self, rnode: R_Node) -> None:
        pass

    def add_entity(self, entity_id: UID, entity_bbox: BBox) -> None:
        pass

    def add_rnode(self, parent_rnode: R_Node) -> None:
        pass

    def find_rnode(self, bbox: BBox) -> None:
        pass

    def find_leaves(self, rnode: R_Node) -> List[R_Node]:
        pass

    def set_r_node_free(self, rnode: R_Node) -> None:
        pass

    def set_r_entity_free(self, enitity_id: UID) -> None:
        pass
