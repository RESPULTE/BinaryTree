from enum import auto
from typing import Dict, List, Optional, Tuple, Union

from ._r_node import R_Entity, R_Node, get_sibling, get_children

from ..utils import BBox, get_area, get_bounding_area, is_inscribed, is_intersecting
from ..type_hints import UID


def get_best_fitting_rnode(rnode_1: R_Node, rnode_2: R_Node,
                           tbbox: BBox) -> Union[R_Node, None]:
    bbox_1 = get_bounding_area(rnode_1.bbox, tbbox)
    bbox_2 = get_bounding_area(rnode_2.bbox, tbbox)

    enlargement_1 = bbox_1 - get_area(rnode_1.bbox)
    enlargement_2 = bbox_2 - get_area(rnode_2.bbox)

    if enlargement_1 != enlargement_2:
        return rnode_1 if enlargement_1 < enlargement_2 else rnode_2

    if bbox_1 != bbox_2:
        return rnode_1 if bbox_1 < bbox_2 else rnode_2

    return None


# get the min max capacity right
# check the condense tree method's correctness
# test using PIL, somehow
# autoid
class RTree:

    def __init__(self, node_capacity: int = 4, auto_id: bool = False) -> None:
        self.node_max_capacity = node_capacity
        self.node_min_capacity = node_capacity // 2
        self.auto_id = auto_id

        self.root: R_Node = R_Node()

        # for fast access/query
        self.all_entity: Dict[UID, R_Entity] = {}
        # might add another list for all_rnode
        # if the pointers are at risk of being garbage collected

        self._free_node = None
        self._free_entity = None

    def insert(self, entity_id: UID, entity_bbox: BBox) -> None:
        # restructure, set special case for leaf/empty root node
        if self.root.is_leaf:
            target_node = self.root
        else:
            target_node = self.find_leaves(entity_bbox=entity_bbox)

        self.add_entity(entity_id, entity_bbox, target_node)
        self.check_insertion(target_node)

    def check_insertion(self, rnode: R_Node) -> None:
        if rnode.total_child <= self.node_max_capacity:
            self.condense_tree(rnode)
            return
        self.traversal_split(rnode)

    def traversal_split(self, rnode: R_Node) -> None:
        # change to the quadratic solution for better result
        all_children = get_children(rnode)
        all_children.sort(key=lambda e: (e.bbox.x, e.bbox.y))

        leftmost_child = all_children.pop(0)
        rightmost_child = all_children.pop(-1)

        node_1, node_2 = self.split_rnode(rnode)
        parent_node = rnode.parent_node
        self.reallocate_child(node_1, leftmost_child)
        self.reallocate_child(node_2, rightmost_child)

        while all_children:

            child = all_children.pop()

            target_rnode = get_best_fitting_rnode(node_1, node_2, child.bbox)

            # ensure that each node has the min required entities
            if not target_rnode or len(all_children) <= self.node_min_capacity:
                target_rnode = node_2
                if node_1.total_child < node_2.total_child:
                    target_rnode = node_1

            self.reallocate_child(target_rnode, child)

        # might remove
        parent_node.resize(node_1.bbox, node_2.bbox)
        self.check_insertion(parent_node)

    def reallocate_child(self, p_rnode: R_Node, child: Union[R_Node,
                                                             R_Entity]) -> None:
        # might restructure
        child.parent_node = p_rnode

        last_child = p_rnode.last_child
        if last_child:
            last_child.sibling_node = child
        else:
            p_rnode.child_node = child

        p_rnode.total_child += 1
        p_rnode.resize(child.bbox)

    def split_rnode(self, rnode: R_Node) -> Tuple[R_Node, R_Node]:
        if not rnode.parent_node:
            new_root = R_Node(child_node=rnode, bbox=rnode.bbox, total_child=2)
            rnode.parent_node = new_root
            self.root = new_root

        new_sibling = R_Node(sibling_node=rnode.sibling_node,
                             parent_node=rnode.parent_node)

        for child in get_children(rnode):
            child.sibling_node = None

        rnode.update(sibling_node=new_sibling,
                     bbox=None,
                     child_node=None,
                     total_child=0)

        return rnode, new_sibling

    def delete(self, entity_id: UID) -> None:
        if entity_id not in self.all_entity:
            raise ValueError(f"{entity_id} is not in {type(self).__name__}")
        entity = self.all_entity[entity_id]
        leaf_owner = entity.parent_node
        self.set_node_free(entity)
        self.condense_tree(leaf_owner)

    def clear(self, rm_cached: bool = False) -> None:
        if rm_cached:
            self._free_entity = None
            self._free_node = None

        [self.delete(eid) for eid in self.all_entity]

    def query(self, bbox: BBox) -> List[UID]:

        def traversal_query(node: R_Node, entity_ids: List[UID], tbbox: BBox) -> List[UID]:
            if node.is_branch:
                for subbranch in get_children(node):
                    if is_intersecting(subbranch.bbox, tbbox):
                        traversal_query(subbranch, entity_ids, tbbox)
            else:
                for entity in get_children(node):
                    if is_intersecting(entity.bbox, tbbox):
                        entity_ids.append(entity.uid)

            return entity_ids

        return traversal_query(self.root, [], BBox(*bbox))

    def add_entity(self, entity_id: UID, entity_bbox: BBox,
                   rnode: R_Node) -> None:
        if rnode.is_branch:
            raise ValueError('insertion of entity should only be done for a leaf node')

        entity_bbox = BBox(*entity_bbox)
        new_entity = R_Entity(
            uid=entity_id,
            bbox=entity_bbox,
            parent_node=rnode,
        )

        self.all_entity[entity_id] = new_entity
        last_child = rnode.last_child

        if last_child:
            last_child.sibling_node = new_entity
        else:
            rnode.child_node = new_entity

        rnode.resize(entity_bbox)
        rnode.total_child += 1

    def find_rnode(self, bbox: BBox) -> R_Node:
        to_process: List[R_Node] = [self.root]
        candidates: List[R_Node] = []
        while to_process:

            node = to_process.pop()

            if isinstance(node, R_Entity):
                continue

            if is_inscribed(node.bbox, bbox):
                to_process.extend(get_children(node))
                candidates.append(node)

        return min(candidates, key=lambda rnode: rnode.area)

    def find_leaves(
            self,
            rnode: Optional[R_Node] = None,
            entity_bbox: Optional[BBox] = None) -> Union[R_Node, List[R_Node]]:

        def find_leaf_by_bbox(rnode: R_Node, ebbox: BBox) -> R_Node:
            # getting the node that generates the least amount of 'dead' space
            # i.e empty space
            all_sibs: List[R_Node] = get_sibling(rnode)
            target_node: R_Node = min(all_sibs, key=lambda s: get_bounding_area(s, ebbox) - s.area)

            if rnode.is_branch:
                return find_leaf_by_bbox(target_node.child_node, ebbox)
            return target_node

        def find_all_leaves(rnode: R_Node) -> List[R_Node]:
            if rnode.is_leaf:
                return rnode
            return [find_all_leaves(c) for c in get_children(rnode)]

        if not rnode and not entity_bbox:
            rnode = self.root

        if rnode:
            return find_all_leaves(rnode)
        return find_leaf_by_bbox(self.root, entity_bbox)

    def set_node_free(self, node: Union[R_Entity, R_Node]) -> None:
        parent_rnode = node.parent_node

        if parent_rnode.child_node is node:
            parent_rnode.child_node = node.sibling_node
        else:
            sibling = next(filter(lambda s: s.sibling_node is node, get_sibling(node)))
            sibling.sibling_node = node.sibling_node

        if isinstance(node, R_Entity):
            node.set_free(self._free_entity)
            self._free_entity = node
        else:
            node.set_free(self._free_node)
            self._free_node = node

        parent_rnode.total_child -= 1

    def condense_tree(self, rnode: R_Node) -> None:
        # restructure, correctness check
        entity_to_reallocate: List[R_Entity] = []
        while rnode.parent_node:

            # underflowed nodes
            if rnode.total_child < self.node_min_capacity:
                entity_to_reallocate.append(get_children(rnode))
                self.set_node_free(rnode)
                continue

            # why: if c not in entity_to_reallocate
            child_bboxes = [
                c.bbox for c in get_children(rnode)
                if c not in entity_to_reallocate
            ]
            rnode.resize(*child_bboxes)
            rnode = rnode.parent_node

        for entity in entity_to_reallocate:
            self.insert(entity.uid, entity.bbox)
