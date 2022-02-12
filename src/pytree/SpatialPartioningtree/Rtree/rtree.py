from typing import Dict, List, Optional, Tuple, Union

from ..utils import BBox, generate_id, within_radius
from ..type_hints import UID, Point

# tons of optimisation to be done
# the allocation of the nodes after the node splitting
# some clean ups for the core methods to make things a lil more readable


def get_sibling(node: Union['R_Node', 'R_Entity']) -> List[Union['R_Node', 'R_Entity']]:
    siblings = []
    while node:
        siblings.append(node)
        node = node.sibling

    return siblings


def get_children(node: 'R_Node') -> List[Union['R_Node', 'R_Entity']]:
    return get_sibling(node.child)


def get_all_children(node: 'R_Node') -> List[Union['R_Node', 'R_Entity']]:
    children = []
    to_process = [node]
    while to_process:
        node = to_process.pop()

        child_nodes = get_children(node)

        children.append(child_nodes)
        to_process.append(child_nodes)

    return children


def get_best_fitting_rnode(
    rnode_1: 'R_Node',
    rnode_2: 'R_Node',
    tbbox: BBox
) -> Union['R_Node', None]:

    super_bbox_1_area = BBox.get_super_bbox(rnode_1.bbox, tbbox).area
    super_bbox_2_area = BBox.get_super_bbox(rnode_2.bbox, tbbox).area

    enlargement_1 = super_bbox_1_area - rnode_1.bbox.area
    enlargement_2 = super_bbox_2_area - rnode_2.bbox.area

    if enlargement_1 != enlargement_2:
        return rnode_1 if enlargement_1 < enlargement_2 else rnode_2

    if super_bbox_1_area != super_bbox_2_area:
        return rnode_1 if super_bbox_1_area < super_bbox_2_area else rnode_2

    return None


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
        self.bbox = BBox.get_super_bbox(*bbox, self.bbox) \
            if self.bbox else BBox.get_super_bbox(*bbox)

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


class RTree:

    def __init__(self,
                 node_capacity: int = 4,
                 max_boundary: Tuple[int, int] = None,
                 auto_id: bool = False
                 ) -> None:
        self.node_max_capacity = node_capacity
        self.node_min_capacity = node_capacity // 2
        self.max_boundary = BBox(0, 0, *max_boundary) if max_boundary else None
        self.auto_id = auto_id

        self.root: R_Node = R_Node()
        self.all_entity: Dict[UID, R_Entity] = {}

        self._free_node = None
        self._free_entity = None

    @property
    def height(self):
        '''recursively get the height of the node'''
        def traversal_counter(node) -> int:
            if isinstance(node, R_Entity):
                return -1
            return 1 + max(traversal_counter(c) for c in get_children(node))

        return traversal_counter(self.root)

    @classmethod
    def fill_tree(cls,
                  entities: List[Union[BBox, Tuple[BBox, UID]]],
                  node_capacity: int = 4,
                  auto_id: bool = True
                  ) -> 'RTree':
        rtree = cls(node_capacity=node_capacity, auto_id=auto_id)

        if any(len(entity) == 2 for entity in entities):
            entities_with_id = [entity for entity in entities if len(entity) == 2]
            for entity_bbox, entity_id in entities_with_id:
                entities.remove((entity_bbox, entity_id))
                rtree.insert(entity_bbox, entity_id)

        for entity in entities:
            rtree.insert(entity)

        return rtree

    def extend(self, entities: List[Union[BBox, Tuple[BBox, UID]]]) -> None:
        if any(len(entity) == 2 for entity in entities):
            entities_with_id = [entity for entity in entities if len(entity) == 2]
            for entity_bbox, entity_id in entities_with_id:
                entities.remove((entity_bbox, entity_id))
                self.insert(entity_bbox, entity_id)

        for entity in entities:
            self.insert(entity)

    def insert(self, entity_bbox: BBox, entity_id: Optional[UID] = None) -> None:

        def best_leaf_finder(rnode: R_Node):
            # getting the node that generates the least amount of 'dead' space
            all_sibs: List[R_Node] = get_sibling(rnode)
            target_node: R_Node = min(all_sibs,
                                      key=lambda s:
                                      BBox.get_super_bbox(s.bbox, entity_bbox).area -
                                      s.bbox.area)
            if rnode.is_branch:
                return best_leaf_finder(target_node.child)
            return target_node

        if entity_id in self.all_entity.keys():
            raise ValueError("entity_id already exists in the tree")

        if isinstance(entity_id, type(None)):
            if not self.auto_id:
                raise ValueError("set RTree's auto_id to True or provide ids for the entity")
            entity_id = generate_id(self.all_entity.keys())

        entity_bbox = BBox(*entity_bbox)

        if self.max_boundary and not entity_bbox.is_within(self.max_boundary):
            raise ValueError("entity out of bound")

        if self.root.is_leaf:
            target_node = self.root
        else:
            target_node = best_leaf_finder(self.root)

        self.__add_entity(entity_id, entity_bbox, target_node)
        self.__check_insertion(target_node)

    def delete(self, entity_id: UID) -> None:
        if entity_id not in self.all_entity:
            raise ValueError(f"{entity_id} is not in {type(self).__name__}")
        entity = self.all_entity[entity_id]
        leaf_owner = entity.parent
        self.__set_node_free(entity)
        self._condense_tree(leaf_owner)

    def clear(self, rm_cached: bool = False) -> None:
        if rm_cached:
            self._free_entity = None
            self._free_node = None
        for eid in self.all_entity.keys():
            self.delete(eid)

    def query_intersection(self, bbox: BBox) -> List[UID]:

        def traversal_query(node: R_Node, entity_ids: List[UID], tbbox: BBox) -> List[UID]:
            if node.is_branch:
                for subbranch in get_children(node):
                    if subbranch.bbox.intersect(tbbox):
                        traversal_query(subbranch, entity_ids, tbbox)
            else:
                for entity in get_children(node):
                    if entity.bbox.intersect(tbbox):
                        entity_ids.append(entity.uid)

            return entity_ids

        bbox = self.root.bbox if not bbox else BBox(*bbox)
        return traversal_query(self.root, [], bbox)

    def query_entity(self,
                     bbox: Optional[BBox] = None,
                     radius: Optional[Tuple[Point, float]] = None
                     ) -> List[UID]:
        if not bbox and not radius:
            raise ValueError("bbox or radius must be specified")

        if not bbox:
            x, y = radius[0][0] - radius[1], radius[0][1] - radius[1]
            size = radius[1] * 2
            bbox = (x, y, size, size)

        bbox = BBox(*bbox)
        if not bbox.is_within(self.root.bbox):
            bbox.trim_ip(self.root.bbox)

        found_entities: List[R_Entity] = []
        for rnode in self._find_leaves(bbox=bbox):
            for entity in get_children(rnode):
                if entity.bbox.intersect(bbox):
                    found_entities.append(entity)

        if not radius:
            return [e.uid for e in found_entities]

        return [
            e.uid for e in found_entities
            if within_radius(
                origin_point=radius[0],
                radius=radius[1],
                bbox=e.bbox
            )
        ]

    def _find_rnode(self, bbox: BBox) -> R_Node:
        to_process: List[R_Node] = [self.root]
        candidates: List[R_Node] = []
        while to_process:

            node = to_process.pop()

            if isinstance(node, R_Entity):
                continue

            if bbox.is_within(node.bbox):
                to_process.extend(get_children(node))
                candidates.append(node)

        return min(candidates, key=lambda rnode: rnode.bbox.area, default=None)

    def _find_leaves(self, rnode: R_Node = None, bbox: BBox = None) -> List[R_Node]:

        def find_all_leaves(rnode: R_Node, leaves: list) -> List[R_Node]:
            if rnode.is_leaf:
                leaves.append(rnode)
            else:
                for child in get_children(rnode):
                    find_all_leaves(child, leaves)

            return leaves

        if not rnode and not bbox:
            rnode = self.root
        elif not rnode:
            rnode = self._find_rnode(bbox)

        return find_all_leaves(rnode, [])

    def _condense_tree(self, rnode: R_Node) -> None:
        entity_to_reallocate: List[R_Entity] = []
        while rnode.parent:

            # underflowed nodes
            if rnode.total_child < self.node_min_capacity:
                entity_to_reallocate.extend(get_children(rnode))
                self.__set_node_free(rnode)
                continue

            child_bboxes = [c.bbox for c in get_children(rnode)]
            rnode.resize(*child_bboxes)
            rnode = rnode.parent

        for entity in entity_to_reallocate:
            self.insert(entity.uid, entity.bbox)

    def __add_entity(self, entity_id: UID, entity_bbox: BBox,
                     rnode: R_Node) -> None:
        if rnode.is_branch:
            raise ValueError('insertion of entity should only be done for a leaf node')

        entity_bbox = BBox(*entity_bbox)
        new_entity = R_Entity(
            uid=entity_id,
            bbox=entity_bbox,
            parent=rnode,
        )

        self.all_entity[entity_id] = new_entity
        last_child = rnode.last_child

        if last_child:
            last_child.sibling = new_entity
        else:
            rnode.child = new_entity

        rnode.resize(entity_bbox)
        rnode.total_child += 1

    def __check_insertion(self, rnode: R_Node) -> None:
        if rnode.total_child <= self.node_max_capacity:
            self._condense_tree(rnode)
            return
        self.__traversal_split(rnode)

    def __traversal_split(self, rnode: R_Node) -> None:
        # change to the quadratic solution for better result
        all_children = get_children(rnode)
        all_children.sort(key=lambda e: (e.bbox.x, e.bbox.y))

        leftmost_child = all_children.pop(0)
        rightmost_child = all_children.pop(-1)

        node_1, node_2 = self.__split_rnode(rnode)
        parent = rnode.parent
        self.__reallocate_child(node_1, leftmost_child)
        self.__reallocate_child(node_2, rightmost_child)

        while all_children:

            child = all_children.pop()

            target_rnode = get_best_fitting_rnode(node_1, node_2, child.bbox)

            # ensure that each node has the min required entities
            if not target_rnode or len(all_children) <= self.node_min_capacity:
                target_rnode = node_2
                if node_1.total_child < node_2.total_child:
                    target_rnode = node_1

            self.__reallocate_child(target_rnode, child)

        # might remove
        parent.resize(node_1.bbox, node_2.bbox)
        self.__check_insertion(parent)

    def __reallocate_child(self, p_rnode: R_Node, child: Union[R_Node, R_Entity]) -> None:
        child.parent = p_rnode

        last_child = p_rnode.last_child
        if last_child:
            last_child.sibling = child
        else:
            p_rnode.child = child

        p_rnode.total_child += 1
        p_rnode.resize(child.bbox)

    # clean up
    def __split_rnode(self, rnode: R_Node) -> Tuple[R_Node, R_Node]:
        if not rnode.parent:
            new_root = R_Node(child=rnode, bbox=rnode.bbox, total_child=2)
            rnode.parent = new_root
            self.root = new_root
        else:
            rnode.parent.total_child += 1

        new_sibling = R_Node(sibling=rnode.sibling,
                             parent=rnode.parent)

        for child in get_children(rnode):
            child.sibling = None

        rnode.update(sibling=new_sibling,
                     bbox=None,
                     child=None,
                     total_child=0)

        return rnode, new_sibling

    # clean up

    def __set_node_free(self, node: Union[R_Entity, R_Node]) -> None:
        parent_rnode = node.parent

        if parent_rnode.child is node:
            parent_rnode.child = node.sibling
        else:
            sibling = next(filter(lambda s: s.sibling is node, get_children(parent_rnode)))
            sibling.sibling = node.sibling

        if isinstance(node, R_Entity):
            node.set_free(self._free_entity)
            self._free_entity = node
        else:
            node.set_free(self._free_node)
            self._free_node = node

        parent_rnode.total_child -= 1

    def __repr__(self):
        return "to be implemented"

    def __bool__(self):
        return self.all_entity != {}

    def __contains__(self, entity_id: UID):
        return entity_id in self.all_entity.keys()

    def __iter__(self):
        return iter(self.all_entity.items())
