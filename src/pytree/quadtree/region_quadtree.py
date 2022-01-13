from typing import Optional, List, Union, Dict, Tuple

from .utils import is_inscribed, is_intersecting, split_box, BBox
from .type_hints import UID


class QuadEntityNode:

    __slots__ = ["next_index", "entity_id", "owner_node"]

    def __init__(self,
                 entity_id: int = -1,
                 next_index: int = -1,
                 owner_node: "QuadNode" = None):
        self.entity_id = entity_id
        self.next_index = next_index
        self.owner_node = owner_node

    @property
    def in_use(self):
        return self.entity_id and self.owner_node

    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]

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


class QuadNode:

    __slots__ = ["first_child", "total_entity", "parent_index"]

    def __init__(
        self,
        first_child: int = -1,
        total_entity: int = 0,
        parent_index: "QuadNode" = -1,
    ):
        self.first_child = first_child
        self.total_entity = total_entity
        self.parent_index = parent_index

    @property
    def is_branch(self):
        return self.total_entity == -1

    @property
    def is_leaf(self):
        return self.total_entity >= 0

    @property
    def in_use(self):
        return self.parent_index and self.total_entity

    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]

    def __str__(self):
        return f" \
        QuadNode(first_child={self.first_child}, \
        total_entity={self.total_entity}, \
        parent_index={self.parent_index})"

    def __repr__(self):
        return f" \
        QuadNode(first_child={self.first_child}, \
        total_entity={self.total_entity}, \
        parent_index={self.parent_index})"


class QuadTree:

    def __init__(
        self,
        bbox: BBox,
        capacity: int = 2,
        max_depth: int = 12,
        max_division: int = 3,
        auto_id: bool = False,
    ):

        if not isinstance(bbox, (type(None), tuple)) or not isinstance(
                bbox[0], (int, float)):
            raise ValueError(
                "bounding box of entity must be a tuple of 4 numbers ")

        if not isinstance(capacity, int):
            raise ValueError("capacity of tree must be an integers")

        self.bbox = BBox(*bbox)
        self.capacity = capacity
        self.auto_id = auto_id
        self.max_depth = max_depth
        self.max_division = max_division

        self._free_quad_node_index = -1
        self._free_entity_node_index = -1

        self._num_quad_node_in_use = 1
        self._num_entity_node_in_use = 0

        self.all_quad_node: List[QuadNode] = []
        self.all_entity: Dict[UID, BBox] = {}
        self.all_entity_node: List[QuadEntityNode] = []

        self.cleaned = True

        self.all_quad_node.append(QuadNode())

    @property
    def num_entity(self):
        return len(self.all_entity)

    @property
    def num_quad_node_in_use(self):
        return self._num_quad_node_in_use

    @property
    def num_entity_node_in_use(self):
        return self._num_entity_node_in_use

    @property
    def num_quad_node(self):
        return len(self.all_quad_node)

    @property
    def num_entity_node(self):
        return len(self.all_entity_node)

    @property
    def real_depth(self):
        """
        returns the actual depth of the quadtree
        * including all the unused nodes
        """
        return (len(self.all_quad_node) - 1) // 4

    @property
    def depth(self):
        """
        returns the apparent depth of the quadtree
        * not including all the unused nodes
        """
        return (self._num_quad_node_in_use - 1) // 4

    @property
    def root(self):
        """returns the first quad node, for conveience"""
        return self.all_quad_node[0]

    @classmethod
    def fill_tree(
        cls,
        bbox: "BBox",
        entities: Optional[Union[List[Tuple["UID", "BBox"]],
                                 List[Tuple["UID"]]]] = None,
        size: int = 0,
        capacity: Optional[int] = 1,
        auto_id: Optional[bool] = False,
    ) -> "QuadTree":

        if not any([entities, bbox]):
            raise ValueError(
                "requires at least 1 of the 2 arguements: 'size' & 'entities'")

        quadtree = cls(bbox, capacity, auto_id)

        [quadtree.insert(entity_data) for entity_data in entities]

        return quadtree

    def get_bbox(self,
                 qnode: QuadNode,
                 index: Optional[bool] = False) -> Tuple[int, BBox]:
        """
        returns the bounding box of a quad node
        depending on the position of the quad node in the quad tree
        """
        if qnode == self.root:
            return (0, self.bbox)

        qnode_index = self.all_quad_node.index(qnode)
        quadrants = [(qnode_index - 1) % 4]

        # keep looping until the root node is reached
        # keep track of the quadrant of each node that has been traversed
        while qnode.parent_index != 0:
            quadrants.append((qnode.parent_index - 1) % 4)
            qnode = self.all_quad_node[qnode.parent_index]

        # split the main bounding box in order of the tracked quadrants
        # the quadrants list is not to be reversed
        # -> the node is traversed bottom-up
        # no need to keep a list of splitted bbox
        # -> the last bounding bbox will be the node's bbox
        tbbox = self.bbox
        for quadrant_index in quadrants:
            for ind, quad in enumerate(split_box(tbbox)):
                if ind == quadrant_index:
                    tbbox = quad

        return (qnode_index, tbbox)

    def find_quad_node(
        self,
        bbox: BBox,
        index: Optional[bool] = False
    ) -> Union[Tuple[QuadNode, BBox], Tuple[int, QuadNode, BBox]]:
        """
        returns a quad node that completely encompasses a given bbox
        the extra index paramter is also for convenience sake
        """
        to_process = [(0, self.bbox)]
        candidates = []

        while to_process:

            qindex, qbbox = to_process.pop()
            qnode = self.all_quad_node[qindex]

            if not qnode.in_use:
                continue

            candidates.append((qindex, qnode, qbbox))

            if qnode.is_leaf:
                continue

            for ind, quadrant in enumerate(split_box(qbbox)):
                # compare the area of the splitted quadrant and bbox
                # consider the quadrant if its area is >= the bbox's area
                if is_intersecting(bbox, quadrant) and is_inscribed(
                        bbox, quadrant):
                    to_process.append((qnode.first_child + ind, quadrant))

        target_qnode = min(candidates,
                           key=lambda qnode: qnode[2].w * qnode[2].h)
        return target_qnode if index else (target_qnode[1], target_qnode[2])

    def find_leaves(
        self,
        qnode: Optional[QuadNode] = None,
        bbox: Optional[BBox] = None,
        index: Optional[bool] = False,
    ) -> Union[List[Tuple[QuadNode, BBox]], List[Tuple[int, QuadNode, BBox]]]:
        """
        find the all the leaves that's encompassed by:
        - a quad node
        - a bounding bbox
        returns the found quad node, its bbox and its index (optional)
        """

        if not qnode and not bbox:
            raise ValueError(
                "at least one or the other is required, 'qnode' or 'bbox'")
        if qnode and bbox:
            raise ValueError(
                "only one or the other is allowed, 'qnode' or 'bbox'")

        if qnode:
            qindex, qbbox = self.get_bbox(qnode=qnode, index=True)

        if bbox:
            qindex, _, qbbox = self.find_quad_node(bbox=bbox, index=True)

        to_process = [(qindex, qbbox)]

        bounded_leaves = []

        while to_process:

            qindex, qbbox = to_process.pop()
            qnode = self.all_quad_node[qindex]

            if not qnode.in_use:
                continue

            if qnode.is_leaf:
                quad_data = (qindex, qnode, qbbox) if index else (qnode, qbbox)
                bounded_leaves.append(quad_data)
                continue

            for ind, quadrant in enumerate(split_box(qbbox)):
                if is_intersecting(qbbox, quadrant):
                    to_process.append((qnode.first_child + ind, quadrant))

        return bounded_leaves

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
        conditions = (qnode, eid, bbox)
        if not any(conditions):
            raise ValueError(
                "at least one or the other is required, 'qnode' or 'eid'")
        if all(conditions) or sum(1 for c in conditions if bool(c)) > 1:
            raise ValueError(
                "only one or the other is allowed, 'qnode' or 'eid'")

        ebbox = self.all_entity[eid] if eid else bbox
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

    def query(
        self,
        bbox: Optional[BBox] = None,
    ) -> List[Dict[UID, UID]]:

        intersecting_entities = {}

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

    def delete(self, eid: UID) -> None:
        """remove the entity with the given entity id from the tree"""
        if eid not in self.all_entity:
            raise ValueError(f"{eid} is not in the entity_list")
        self.set_free_entity_nodes(self.find_entity_node(eid=eid, index=True))
        self.all_entity = {
            k: v
            for k, v in self.all_entity.items() if k != eid
        }
        self.cleaned = False

    def clean_up(self) -> None:

        def clean_up_quad_node(qnode: QuadNode) -> None:
            # if the node is not in-use:
            # -> the node has been set free, the work is done
            # if the node is not an empty leaf node
            if not qnode.in_use or (qnode.is_leaf and qnode.total_entity > 0):
                return 0

            if qnode.is_branch:
                # recursively call this function upon all it's other 4 children
                # if all of its children have 0 entity nodes in it,
                # -> free all of its children and set it as an empty leaf
                # reset the node's first_child to 1 if its a root node,
                # -> or else it'll mess up future node allocations
                first_child_index = qnode.first_child
                if (sum(
                        clean_up_quad_node(self.all_quad_node[qnode.first_child
                                                              + i])
                        for i in range(4)) == 4):
                    self.set_free_quad_node(
                        self.all_quad_node[first_child_index],
                        first_child_index)
                    if qnode == self.root:
                        qnode.first_child = 1

            # return 1 since the node is an empty leaf
            return 1

        clean_up_quad_node(self.root)

    def clear(self, rm_cached=False) -> None:
        self.all_entity.clear()

        if rm_cached:
            self.all_quad_node = self.all_quad_node[0:1]
            self.all_entity_node.clear()
            return

        [self.delete(eid) for eid in self.all_entity.keys()]
        self.clean_up()

    def set_free_entity_nodes(
            self, indexed_entity_nodes: List[Tuple[int,
                                                   QuadEntityNode]]) -> None:
        for ind, en in indexed_entity_nodes:
            owner_qnode = en.owner_node
            if owner_qnode.first_child == ind:
                owner_qnode.first_child = en.next_index

            else:
                related_en = next(
                    filter(
                        lambda en: en.next_index == ind,
                        self.find_entity_node(qnode=owner_qnode),
                    ))
                related_en.next_index = en.next_index

            en.update(next_index=self._free_entity_node_index,
                      entity_id=None,
                      owner_node=None)

            self._free_entity_node_index = ind
            self._num_entity_node_in_use -= 1
            owner_qnode.total_entity -= 1

    def set_free_quad_node(self, qnode: QuadNode, qindex: int) -> None:
        if (qindex - 1) % 4 != 0:
            raise ValueError(f"the liberation should happen to the \
                  first child not the '{(qindex - 1) % 4}' child")

        parent_node = self.all_quad_node[qnode.parent_index]

        for i in range(4):
            self.all_quad_node[parent_node.first_child + i].update(
                first_child=self._free_quad_node_index,
                total_entity=None,
                parent_index=None,
            )

        self._free_quad_node_index = qindex
        self._num_quad_node_in_use -= 4
        parent_node.first_child = -1
        parent_node.total_entity = 0

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

    def set_branch(self, qnode: QuadNode, qindex: int):
        qnode.total_entity = -1

        self._num_quad_node_in_use += 4

        if self._free_quad_node_index == -1:
            # create 4 more quad node's and set the node's first child index
            qnode.first_child = len(self.all_quad_node)
            [
                self.all_quad_node.append(QuadNode(parent_index=qindex))
                for i in range(4)
            ]
            return

        # allocate that free node to the current node
        qnode.first_child = self._free_quad_node_index

        next_free_quad_node_index = self.all_quad_node[
            qnode.first_child].first_child

        for i in range(4):
            child_index = self._free_quad_node_index + i
            self.all_quad_node[child_index].update(first_child=-1,
                                                   total_entity=0,
                                                   parent_index=qindex)

        # reset the free node's index to the free node's child
        # which should either be -1 if there's no more free node
        # or another node's index
        self._free_quad_node_index = next_free_quad_node_index

    # check correctness
    # repeating values in the query
    def insert(self,
               entity_bbox: BBox,
               entity_id: Optional[UID] = None) -> None:

        def division_insert(
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

                if (current_child.total_entity <= self.capacity
                        or num_division < self.max_division):
                    continue

                indexed_entity_nodes = self.find_entity_node(current_child,
                                                             index=True)
                bounded_entities = [(en.entity_id,
                                     self.all_entity[en.entity_id])
                                    for _, en in indexed_entity_nodes]
                self.set_free_entity_nodes(indexed_entity_nodes)

                division_insert(
                    current_index,
                    current_child,
                    quadrant,
                    bounded_entities,
                    num_division + 1,
                )

        if not all(isinstance(num, (int, float)) for num in entity_bbox):
            raise ValueError(
                "bounding box of entity must be a tuple of 4 numbers ")

        if isinstance(entity_id, type(None)) and not self.auto_id:
            raise ValueError(
                "set QuadTree's auto_id to True or provide ids for the entity")

        if self.depth > self.max_depth:
            raise ValueError(
                f"Quadtree's depth has exceeded the maximum depth of {self.max_depth} \
                \ncurrent quadtree's depth: {self.depth}")

        if not self.cleaned:
            self.clean_up()
            self.cleaned = True

        if isinstance(entity_id, type(None)):
            int_id = filter(lambda id: isinstance(id, (int, float)),
                            self.all_entity.keys())
            if not int_id:
                int_id.append(0)
            entity_id = max(int_id) + 1 if self.all_entity else 0

        if not isinstance(entity_bbox, BBox):
            entity_bbox = BBox(*entity_bbox)

        self.all_entity[entity_id] = entity_bbox

        for qindex, qnode, qbbox in self.find_leaves(bbox=entity_bbox,
                                                     index=True):
            self.add_entity_node(qnode, entity_id)

            if qnode.total_entity <= self.capacity:
                continue

            indexed_entity_nodes = self.find_entity_node(qnode=qnode,
                                                         index=True)
            bounded_entities = [(en.entity_id, self.all_entity[en.entity_id])
                                for _, en in indexed_entity_nodes]
            self.set_free_entity_nodes(indexed_entity_nodes)
            division_insert(qindex, qnode, qbbox, bounded_entities)

    def __repr__(self) -> str:
        return f"{type(self).__name__}( \
        num_entity: {self.num_entity}, \
        num_quad_node: {len(self.all_quad_node)} \
        num_entity_node: {len(self.all_entity_node)} \
        num_quad_node_in_use: {self.num_quad_node_in_use}, \
        num_entity_node_in_use: {self.num_entity_node_in_use} \
        )"

    def __len__(self) -> int:
        return len(self.all_entity)
