from typing import Iterable, Optional, List, Dict, Set, Tuple, Union

from pytree.SpatialPartioningtree.Quadtree.basequadtree import BaseQuadTree, QuadNode
from pytree.SpatialPartioningtree.utils import BBox, generate_id, within_radius
from pytree.SpatialPartioningtree.type_hints import UID, Point


class QuadEntityNode:

    __slots__ = ["next_index", "entity_id", "owner_node"]

    def __init__(self,
                 entity_id: UID = -1,
                 next_index: int = -1,
                 owner_node: QuadNode = None):
        self.entity_id = entity_id
        self.next_index = next_index
        self.owner_node = owner_node

    @property
    def in_use(self):
        return self.entity_id and self.owner_node

    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]

    def set_free(self, next_free_enode_index: int) -> None:
        self.next_index = next_free_enode_index
        self.entity_id = None
        self.owner_node = None

    def __str__(self):
        return f" \
        QuadEntityNode(next_index={self.next_index}, \
        entity_id={self.entity_id}, \
        owner_node={self.owner_node})"

    def __repr__(self):
        return f" \
        QuadEntityNode(next_index={self.next_index}, \
        entity_id={self.entity_id}, \
        owner_node={self.owner_node})"


class EntityQuadTree(BaseQuadTree):

    def __init__(
        self,
        bbox: BBox,
        node_capacity: int = 2,
        max_depth: int = 12,
        max_division: int = 3,
        auto_id: bool = True,
    ) -> None:

        super().__init__(bbox, max_depth, auto_id)

        if node_capacity < 1:
            raise ValueError("node capacity must be greater than 0")

        self.node_capacity = int(node_capacity)
        self.max_division = int(max_division)

        self.all_entity: Dict[UID, BBox] = {}
        self.all_entity_node: List[QuadEntityNode] = []

        self.__free_entity_node_index = -1
        self.__num_entity_node_in_use = 0

    @property
    def num_entity(self):
        return len(self.all_entity)

    @property
    def num_entity_node(self):
        return len(self.all_entity_node)

    @property
    def num_entity_node_in_use(self):
        return self.__num_entity_node_in_use

    @classmethod
    def fill_tree(cls,
                  entities: List[Union[BBox, Tuple[BBox, UID]]],
                  node_capacity: int = 4,
                  auto_id: bool = True
                  ) -> 'EntityQuadTree':
        eqtree = cls(node_capacity=node_capacity, auto_id=auto_id)

        if any(len(entity) == 2 for entity in entities):
            entities_with_id = [entity for entity in entities if len(entity) == 2]
            for entity_bbox, entity_id in entities_with_id:
                entities.remove((entity_bbox, entity_id))
                eqtree.insert(entity_bbox, entity_id)

        for entity in entities:
            eqtree.insert(entity)

        return eqtree

    def extend(self, entities: List[Union[BBox, Tuple[BBox, UID]]]) -> None:
        if any(len(entity) == 2 for entity in entities):
            entities_with_id = [entity for entity in entities if len(entity) == 2]
            for entity_bbox, entity_id in entities_with_id:
                entities.remove((entity_bbox, entity_id))
                self.insert(entity_bbox, entity_id)

        for entity in entities:
            self.insert(entity)

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

            self._set_branch(qnode, qindex)

            for ind, quadrant in enumerate(qbbox.split()):
                current_index = qnode.first_child + ind
                current_child = self.all_quad_node[current_index]

                for eid, ebbox in entities:
                    if quadrant.intersect(ebbox):
                        self.__add_entity_node(current_child, eid)

                if (current_child.total_entity <= self.node_capacity
                    or num_division > self.max_division):  # noqa
                    continue

                indexed_entity_nodes = self._find_entity_node(qnode=current_child,
                                                              index=True)
                bounded_entities = [(en.entity_id,
                                     self.all_entity[en.entity_id])
                                    for _, en in indexed_entity_nodes]

                self.__set_free_entity_nodes(indexed_entity_nodes)

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

        entity_bbox = BBox(*entity_bbox)

        if not entity_bbox.is_within(self.bbox):
            raise ValueError("entity's bbox is out of bound!")

        if isinstance(entity_id, type(None)):
            if not self.auto_id:
                raise ValueError("set QuadTree's auto_id to True or provide ids for the entity")
            entity_id = generate_id(self.all_entity.keys())

        self.all_entity[entity_id] = entity_bbox

        for qindex, qnode, qbbox in self._find_leaves(bbox=entity_bbox,
                                                      index=True):
            self.__add_entity_node(qnode, entity_id)
            if qnode.total_entity <= self.node_capacity:
                continue

            indexed_entity_nodes = self._find_entity_node(qnode=qnode, index=True)
            bounded_entities = [(en.entity_id, self.all_entity[en.entity_id])
                                for _, en in indexed_entity_nodes]

            self.__set_free_entity_nodes(indexed_entity_nodes)
            split_and_insert(qindex, qnode, qbbox, bounded_entities)

    def delete(self, eid: UID) -> None:
        """remove the entity with the given entity id from the tree"""
        if eid not in self.all_entity:
            raise ValueError(f"{eid} is not in the entity_list")
        self.__set_free_entity_nodes(self._find_entity_node(eid=eid, index=True))
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

    def query_intersection(
        self,
        bbox: Optional[BBox] = None,
        pairing: Optional[bool] = False
    ) -> Union[Dict[UID, Set[UID]], Set[UID]]:

        bbox = self.bbox if not bbox else BBox(*bbox)

        intersecting_entities = {}
        for this_eid in self.query_entity(bbox=bbox):
            this_bbox = self.all_entity[this_eid]
            intersecting_entities[this_eid] = set()

            for en in self._find_entity_node(bbox=this_bbox):
                other_eid = en.entity_id
                other_bbox = self.all_entity[other_eid]

                if other_bbox is this_bbox:
                    continue

                if this_bbox.intersect(other_bbox):
                    intersecting_entities[this_eid].add(other_eid)

        if not pairing:
            temp = list(intersecting_entities.values()).copy()
            intersecting_entities = set()
            for entity_set in temp:
                intersecting_entities.update(entity_set)

        return intersecting_entities

    def query_entity(self,
                     bbox: Optional[BBox] = None,
                     radius: Optional[Tuple[Point, float]] = None
                     ) -> List[UID]:
        if not bbox and not radius:
            return list(self.all_entity.keys())

        if not bbox:
            x, y = radius[0][0] - radius[1], radius[0][1] - radius[1]
            size = radius[1] * 2
            bbox = (x, y, size, size)

        bbox = BBox(*bbox)
        if not bbox.is_within(self.bbox):
            bbox.trim_ip(self.bbox)

        found_entities = list({en.entity_id for en in self._find_entity_node(bbox=bbox)})

        if not radius:
            return found_entities

        return [
            eid for eid in found_entities
            if within_radius(
                origin_point=radius[0],
                radius=radius[1],
                bbox=self.all_entity[eid]
            )
        ]

    def _find_entity_node(
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
                "at least one or the other is required, 'qnode' or 'eid'"
            )

        if all(conditions) or sum(1 for c in conditions if bool(c)) > 1:
            raise ValueError(
                "only one or the other is allowed, 'qnode' or 'eid'"
            )

        ebbox = self.all_entity[eid] if eid is not None else bbox
        qnode = self._find_quad_node(bbox=ebbox)[0] if not qnode else qnode

        entity_nodes: List[QuadEntityNode] = []
        for leaf, _ in self._find_leaves(qnode=qnode):

            next_index = leaf.first_child
            while next_index != -1:
                entity_node = self.all_entity_node[next_index]
                entity_data = (next_index, entity_node) if index else entity_node
                entity_nodes.append(entity_data)
                next_index = entity_node.next_index

        if bbox:
            entity_nodes = [
                en for en in entity_nodes
                if self.all_entity[en.entity_id].intersect(bbox)
            ]
        return entity_nodes

    def __add_entity_node(self, node: QuadNode, entity_id: UID):
        old_index = node.first_child if node.total_entity > 0 else -1

        # update the node's total bounded entity
        node.total_entity += 1

        self.__num_entity_node_in_use += 1

        if self.__free_entity_node_index == -1:
            node.first_child = len(self.all_entity_node)
            self.all_entity_node.append(
                QuadEntityNode(
                    entity_id=entity_id,
                    next_index=old_index,
                    owner_node=node,
                ))
            return

        free_entity_node = self.all_entity_node[self.__free_entity_node_index]

        # set the node's child to the free entity node
        node.first_child = self.__free_entity_node_index

        # reset the free entity node's index
        self.__free_entity_node_index = free_entity_node.next_index

        # update the newly allocated entity node's attribute
        free_entity_node.update(entity_id=entity_id,
                                next_index=old_index,
                                owner_node=node)

    def __set_free_entity_nodes(self, indexed_entities: List[Tuple[int, QuadEntityNode]]) -> None:

        for ind, en in indexed_entities:
            owner_qnode = en.owner_node
            if owner_qnode.first_child == ind:
                owner_qnode.first_child = en.next_index

            else:
                prev_en_node = next(filter(
                    lambda en: en.next_index == ind,
                    self._find_entity_node(qnode=owner_qnode)
                ))
                prev_en_node.next_index = en.next_index

            en.set_free(self.__free_entity_node_index)

            self.__free_entity_node_index = ind
            self.__num_entity_node_in_use -= 1
            owner_qnode.total_entity -= 1

    def __bool__(self) -> bool:
        return self.all_entity != {}

    def __iter__(self) -> Iterable:
        yield from self.all_entity.items()

    def __contains__(self, entity_id: Union[str, int]) -> bool:
        return entity_id in self.all_entity.keys()

    def __repr__(self) -> str:
        return (f"{type(self).__name__}("
                f"num_entity: {self.num_entity}, "
                f"num_quad_node: {len(self.all_quad_node)},"
                f"num_entity_node: {len(self.all_entity_node)}, "
                f"num_quad_node_in_use: {self.num_quad_node_in_use}, "
                f"num_entity_node_in_use: {self.num_entity_node_in_use})"
                )
