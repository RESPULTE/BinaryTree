from typing import List, Union, Tuple

from ..utils import BBox
from ..type_hints import UID


def get_sibling(
    node: Union['R_Node', 'R_Entity']
) -> List[Union['R_Node', 'R_Entity']]:
    siblings = []
    while node:
        siblings.append(node)
        node = node.sibling

    return siblings


def get_children(node: 'R_Node') -> List[Union['R_Node', 'R_Entity']]:
    return get_sibling(node.child)


def get_all_Children(node: 'R_Node') -> List[Union['R_Node', 'R_Entity']]:
    children = []
    to_process = [node]
    while to_process:
        node = to_process.pop()

        child_nodes = get_children(node)

        children.append(child_nodes)
        to_process.append(child_nodes)

    return children


class R_Node:

    __slots__ = ['child', 'sibling', 'parent', 'total_child', 'bbox']

    def __init__(self,
                 child: "R_Node" = None,
                 sibling: "R_Node" = None,
                 parent: "R_Node" = None,
                 total_child: int = 0,
                 bbox: BBox = None) -> None:

        self.child = child
        self.sibling = sibling
        self.parent = parent
        self.total_child = total_child
        self.bbox = bbox

    @property
    def is_leaf(self) -> bool:
        return not isinstance(self.child, type(self))

    @property
    def is_branch(self) -> bool:
        return isinstance(self.child, type(self))

    @property
    def last_child(self) -> Union['R_Entity', 'R_Node']:
        if self.child is None:
            return None
        return get_children(self)[-1]

    def resize(self, *bbox: BBox) -> None:
        self.bbox = BBox.get_super_bbox(*bbox, self.bbox) if self.bbox else \
            BBox.get_super_bbox(*bbox)

    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]

    def set_free(self, next_free_r_node: int) -> None:
        self.child = next_free_r_node
        self.total_child = -1
        self.sibling = None
        self.parent = None
        self.bbox = None

    def __str__(self):
        return f"{type(self).__name__}(bbox={self.bbox}, total_child={self.total_child})"


class R_Entity:

    __slots__ = ["uid", "sibling", "bbox", "parent"]

    def __init__(self,
                 uid: UID = None,
                 bbox: BBox = None,
                 sibling: int = None,
                 parent: R_Node = None):

        self.uid = uid
        self.bbox = bbox
        self.sibling = sibling
        self.parent = parent

    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]

    def set_free(self, next_free_renode: 'R_Entity') -> None:
        self.sibling = next_free_renode
        self.uid = None
        self.bbox = None
        self.parent = None

    def __str__(self):
        return f"{type(self).__name__}(bbox={self.bbox}, uid={self.uid})"
