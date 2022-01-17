from typing import List, Union

from ..utils import BBox


class R_Node:

    __slots__ = ['child_node', 'sibling_node', 'parent_node', 'bbox']

    def __init__(self,
                 child_node: "R_Node" = None,
                 sibling_node: "R_Node" = None,
                 parent_node: "R_Node" = None,
                 bbox: BBox = None) -> None:
        self.child_node = child_node
        self.sibling_node = sibling_node
        self.parent_node = parent_node
        self.bbox = bbox

    @property
    def in_use(self):
        return self.bbox and self.child_node

    @property
    def is_leaf(self):
        return not isinstance(self.child_node, type(self))

    @property
    def is_branch(self):
        return isinstance(self.child_node, type(self))

    @property
    def is_root(self):
        return self.parent_node is None

    def update(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def get_children_bbox(self) -> List[BBox]:
        return [n.bbox for n in get_sibling_node(self.child_node)]

    def set_free(self, next_free_r_node: int) -> None:
        self.child_node = next_free_r_node
        self.sibling_node = None
        self.parent_node = None
        self.bbox = None

    def __str__(self) -> str:
        return f" \
            {type(self).__name__}( \
                child_node={self.child_node}, \
                sibling_node={self.sibling_node}, \
                parent_node={self.parent_node}, \
                bbox={self.bbox} \
            )"

    def __repr__(self) -> str:
        return f" \
            {type(self).__name__}( \
                child_node={self.child_node}, \
                sibling_node={self.sibling_node}, \
                parent_node={self.parent_node}, \
                bbox={self.bbox} \
            )"


class R_Entity:

    __slots__ = ["sibling_node", "enitty_bbox", "owner_node"]

    def __init__(self,
                 enitty_bbox: BBox = None,
                 sibling_node: int = None,
                 owner_node: R_Node = None):
        self.enitty_bbox = enitty_bbox
        self.sibling_node = sibling_node
        self.owner_node = owner_node

    @property
    def in_use(self):
        return self.enitty_bbox and self.owner_node

    def update(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def set_free(self, next_free_renode: 'R_Entity') -> None:
        self.sibling_node = next_free_renode
        self.enitty_bbox = None
        self.owner_node = None

    def __str__(self):
        return f" \
        R_Entity(sibling_node={self.sibling_node}, \
        enitty_bbox={self.enitty_bbox}, \
        owner_node={self.owner_node})"

    def __repr__(self):
        return f" \
        R_Entity(sibling_node={self.sibling_node}, \
        enitty_bbox={self.enitty_bbox}, \
        owner_node={self.owner_node})"


def get_sibling_node(
        node: Union['R_Node',
                    'R_Entity']) -> List[Union['R_Node', 'R_Entity']]:
    siblings = []
    while node.sibling_node:
        siblings.append(node)
        node = node.sibling_node

    return siblings