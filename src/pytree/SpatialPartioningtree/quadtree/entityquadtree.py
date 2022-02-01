from typing import Iterable, Optional, List, Dict, Set, Tuple, Union

from ..utils import BBox, get_area, is_intersecting, split_box, is_inscribed
from ..type_hints import UID

from ._quadnode import QuadEntityNode, QuadNode
from ._quadtree import QuadTree

# POSSIBLE IMPROVEMENTS: weakref for more efficient garbage collection
class EntityBasedQuadTree(QuadTree):

    def __init__(
        self,
        bbox: BBox,
        node_capacity: int = 2,
        max_depth: int = 12,
        max_division: int = 3,
        auto_id: bool = False,
    ) -> None:

        super().__init__(bbox, max_depth, auto_id)

        if get_area(self.bbox) < 0:
            raise ValueError("main bounding box must have a non-zero/negative area")
        if node_capacity < 1:
            raise ValueError("node capacity must be greater than 0")

        self.node_capacity = int(node_capacity)
        self.max_division = int(max_division)

        self.all_entity: Dict[UID, object] = {}
        self.all_entity_node: List[QuadEntityNode] = []

        self._free_entity_node_index = -1
        self._num_entity_node_in_use = 0

    @property
    def num_entity(self):
        return len(self.all_entity)

    @property
    def num_entity_node(self):
        return len(self.all_entity_node)

    @property
    def num_entity_node_in_use(self):
        return self._num_entity_node_in_use

    @classmethod
    def fill_tree(
        cls,
        bbox: "BBox",
        entities: Optional[Union[List[Tuple["UID", "BBox"]],
                                 List[Tuple["UID"]]]] = None,
        capacity: Optional[int] = 1,
        auto_id: Optional[bool] = False,
    ) -> "QuadTree":

        if not any([entities, bbox]):
            raise ValueError(
                "requires at least 1 of the 2 arguements: 'size' & 'entities'")

        quadtree = cls(bbox, capacity, auto_id)

        [quadtree.insert(entity_data) for entity_data in entities]

        return quadtree

    def set_free_entity_nodes(self, indexed_entities: List[Tuple[int, QuadEntityNode]]) -> None:

        for ind, en in indexed_entities:
            owner_qnode = en.owner_node
            if owner_qnode.first_child == ind:
                owner_qnode.first_child = en.next_index

            else:
                prev_en_node = next(filter(
                    lambda en: en.next_index == ind,
                    self.find_entity_node(qnode=owner_qnode)
                ))
                prev_en_node.next_index = en.next_index

            en.set_free(self._free_entity_node_index)

            self._free_entity_node_index = ind
            self._num_entity_node_in_use -= 1
            owner_qnode.total_entity -= 1

    def find_entity_node(
        self,
        qnode: Optional[QuadNode] = None,
        eid: Optional[UID] = None,
        bbox: Optional[BBox] = None,
        index: Optional[bool] = False,
    ) -> Union[List[QuadEntityNode], List[Tuple[int, QuadEntityNode]]]:
        """
        find the all the entity nodes
        - that's encompassed by a quad node
        - that's contained in a given bbox
        - holds a given entity_id
        returns a list of the entity nodes and their index (optional)
        """
        conditions = [c is not None for c in [qnode, eid, bbox]]
        if not any(conditions):
            raise ValueError(
                "at least one or the other is required, 'qnode' or 'eid'")
        if all(conditions) or sum(1 for c in conditions if bool(c)) > 1:
            raise ValueError(
                "only one or the other is allowed, 'qnode' or 'eid'")

        ebbox = self.all_entity[eid] if eid is not None else bbox
        qnode = self.find_quad_node(bbox=ebbox)[0] if not qnode else qnode

        entity_nodes = []
        for leaf, _ in self.find_leaves(qnode=qnode):

            next_index = leaf.first_child
            while next_index != -1:
                entity_node = self.all_entity_node[next_index]
                entity_data = (next_index,
                               entity_node) if index else entity_node
                entity_nodes.append(entity_data)
                next_index = entity_node.next_index

        return entity_nodes

    def add_entity_node(self, node: QuadNode, entity_id: UID):
        old_index = node.first_child if node.total_entity > 0 else -1

        # update the node's total bounded entity
        node.total_entity += 1

        self._num_entity_node_in_use += 1

        if self._free_entity_node_index == -1:
            node.first_child = len(self.all_entity_node)
            self.all_entity_node.append(
                QuadEntityNode(
                    entity_id=entity_id,
                    next_index=old_index,
                    owner_node=node,
                ))
            return

        free_entity_node = self.all_entity_node[self._free_entity_node_index]

        # set the node's child to the free entity node
        node.first_child = self._free_entity_node_index

        # reset the free entity node's index
        self._free_entity_node_index = free_entity_node.next_index

        # update the newly allocated entity node's attribute
        free_entity_node.update(entity_id=entity_id,
                                next_index=old_index,
                                owner_node=node)

    def delete(self, eid: UID) -> None:
        """remove the entity with the given entity id from the tree"""
        if eid not in self.all_entity:
            raise ValueError(f"{eid} is not in the entity_list")
        self.set_free_entity_nodes(self.find_entity_node(eid=eid, index=True))
        self.all_entity = {
            uid: entity
            for uid, entity in self.all_entity.items() if uid != eid
        }
        self.cleaned = False

    def clear(self, rm_cached=False) -> None:
        self.all_entity.clear()

        if rm_cached:
            self.all_quad_node = self.all_quad_node[0:1]
            self.all_entity_node.clear()
            return

        [self.delete(eid=eid) for eid in self.all_entity.keys()]
        self.clean_up()

    def query(
        self,
        bbox: Optional[BBox] = None,
    ) -> Dict[UID, Set[UID]]:

        intersecting_entities: Dict[UID, Set[UID]] = {}

        bbox = self.bbox if not bbox else BBox(*bbox)

        for this_eid, this_bbox in self.all_entity.items():
            intersecting_entities[this_eid] = set()

            for en in self.find_entity_node(bbox=this_bbox):
                other_eid = en.entity_id
                other_bbox = self.all_entity[other_eid]

                if other_bbox is this_bbox:
                    continue

                if is_intersecting(this_bbox, other_bbox):
                    intersecting_entities[this_eid].add(other_eid)

        return intersecting_entities

    def insert(self,
               entity_bbox: BBox,
               entity_id: Optional[UID] = None) -> None:

        def split_and_insert(
            qindex: int,
            qnode: QuadNode,
            qbbox: BBox,
            entities: List[Tuple[UID, BBox]],
            num_division: int = 0,
        ) -> None:

            self.set_branch(qnode, qindex)

            for ind, quadrant in enumerate(split_box(qbbox)):
                current_index = qnode.first_child + ind
                current_child = self.all_quad_node[current_index]

                for eid, ebbox in entities:
                    if is_intersecting(quadrant, ebbox):
                        self.add_entity_node(current_child, eid)

                if (current_child.total_entity <= self.node_capacity
                        or num_division > self.max_division):  # noqa
                    continue

                indexed_entity_nodes = self.find_entity_node(current_child,
                                                             index=True)
                bounded_entities = [(en.entity_id,
                                     self.all_entity[en.entity_id])
                                    for _, en in indexed_entity_nodes]

                self.set_free_entity_nodes(indexed_entity_nodes)

                split_and_insert(
                    current_index,
                    current_child,
                    quadrant,
                    bounded_entities,
                    num_division + 1,
                )

        if isinstance(entity_id, type(None)) and not self.auto_id:
            raise ValueError("set QuadTree's auto_id to True or provide ids for the entity")

        if entity_id in self.all_entity.keys():
            raise ValueError("entity_id already exists in the tree")

        if self.depth > self.max_depth:
            raise ValueError(
                f"Quadtree's depth has exceeded the maximum depth of {self.max_depth}\n \
                  current quadtree's depth: {self.depth}")

        if not self.cleaned:
            self.clean_up()
            self.cleaned = True

        if not isinstance(entity_bbox, BBox):
            entity_bbox = BBox(*entity_bbox)

        if not is_inscribed(entity_bbox, self.bbox):
            raise ValueError("entity's bbox is out of bound!")

        if isinstance(entity_id, type(None)):
            int_id = list(filter(lambda id: isinstance(id, (int, float)), self.all_entity.keys()))
            if not int_id:
                int_id.append(0)
            entity_id = max(int_id) + 1

        self.all_entity[entity_id] = entity_bbox

        for qindex, qnode, qbbox in self.find_leaves(bbox=entity_bbox,
                                                     index=True):
            self.add_entity_node(qnode, entity_id)
            if qnode.total_entity <= self.node_capacity:
                continue

            indexed_entity_nodes = self.find_entity_node(qnode=qnode, index=True)
            bounded_entities = [(en.entity_id, self.all_entity[en.entity_id])
                                for _, en in indexed_entity_nodes]

            self.set_free_entity_nodes(indexed_entity_nodes)
            split_and_insert(qindex, qnode, qbbox, bounded_entities)

    def __bool__(self) -> bool:
        return self.all_entity != {}

    def __iter__(self) -> Iterable:
        yield from self.all_entity.items()

    def __contains__(self, entity_id: Union[str, int]) -> bool:
        return entity_id in self.all_entity.keys()

    def __repr__(self) -> str:
        return f"{type(self).__name__}( \
            num_entity: {self.num_entity}, \
            num_quad_node: {len(self.all_quad_node)}, \
            num_entity_node: {len(self.all_entity_node)}, \
            num_quad_node_in_use: {self.num_quad_node_in_use}, \
            num_entity_node_in_use: {self.num_entity_node_in_use} \
        )"
