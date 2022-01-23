from typing import List, Union, Tuple

from ..utils import BBox, get_super_bbox
from ..type_hints import UID


def get_sibling(
        node: Union['R_Node',
                    'R_Entity']) -> List[Union['R_Node', 'R_Entity']]:
    siblings = []
    while node:
        siblings.append(node)
        node = node.sibling_node

    return siblings


def get_children(node: 'R_Node') -> List[Union['R_Node', 'R_Entity']]:
    return get_sibling(node.child_node)


class R_Node:

    __slots__ = [
        'child_node', 'sibling_node', 'parent_node', 'total_child', 'bbox'
    ]

    def __init__(self,
                 child_node: "R_Node" = None,
                 sibling_node: "R_Node" = None,
                 parent_node: "R_Node" = None,
                 total_child: int = 0,
                 bbox: BBox = None) -> None:

        self.child_node = child_node
        self.sibling_node = sibling_node
        self.parent_node = parent_node
        self.total_child = total_child
        self.bbox = bbox

    @property
    def area(self) -> float:
        return self.bbox.w * self.bbox.h

    @property
    def is_leaf(self) -> bool:
        return not isinstance(self.child_node, type(self))

    @property
    def is_branch(self) -> bool:
        return isinstance(self.child_node, type(self))

    @property
    def is_root(self) -> bool:
        return self.parent_node is None

    @property
    def last_child(self) -> Union['R_Entity', 'R_Node']:
        if self.child_node is None:
            return None
        return get_children(self)[-1]

    def resize(self, *bbox: BBox) -> None:
        self.bbox = get_super_bbox(*bbox, self.bbox) if self.bbox else get_super_bbox(*bbox)

    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]

    def set_free(self, next_free_r_node: int) -> None:
        self.child_node = next_free_r_node
        self.total_child = -1
        self.sibling_node = None
        self.parent_node = None
        self.bbox = None

    def __str__(self):
        return f"{type(self).__name__}(bbox={self.bbox}, total_child={self.total_child})"


class R_Entity:

    __slots__ = ["uid", "sibling_node", "bbox", "parent_node"]

    def __init__(self,
                 uid: UID = None,
                 bbox: BBox = None,
                 sibling_node: int = None,
                 parent_node: R_Node = None):

        self.uid = uid
        self.bbox = bbox
        self.sibling_node = sibling_node
        self.parent_node = parent_node

    @property
    def area(self) -> float:
        return self.bbox.w * self.bbox.h

    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]

    def set_free(self, next_free_renode: 'R_Entity') -> None:
        self.sibling_node = next_free_renode
        self.uid = None
        self.bbox = None
        self.parent_node = None

    def __str__(self):
        return f"{type(self).__name__}(bbox={self.bbox}, uid={self.uid})"
