from collections import deque
from typing import Dict, NewType, Optional, Protocol, Tuple, Tuple, TypeVar, Union, List


# NOTE TO tree: TOPLEFT = (0, 0)
"""
             y1
    (0, 0) ------- (0, 5)
          |       |
   x1     |       |    x2
           -------
    (0, 5)          (5, 5)   
             y2
1. (x, y)
2. x1 < x2
3. y1 < y2
"""
T = TypeVar("T")
UID = NewType("UID", str)

# all the computation should be done in the 'RTree' class
# RTreeEntity & RTreeNode serves it purpose as a data container only
# the root will start out as a branch type and remain as a branch type


class NodeOverflowError(Exception):
    ...


class NodeUnderflowError(Exception):
    ...


class EntityNotFoundError(Exception):
    ...


class DegenerateNodeError(Exception):
    ...


class BBox(Protocol):
    _id: UID
    xmin: int
    ymin: int
    xmax: int
    ymax: int


def intersect(this_bbox: BBox, that_bbox: BBox) -> bool:
    return not (
        this_bbox.xmin >= that_bbox.xmax
        or this_bbox.xmax <= that_bbox.xmin
        or this_bbox.ymin >= that_bbox.ymax
        or this_bbox.ymax <= that_bbox.ymin
    )


def within(this_bbox: BBox, that_bbox: BBox) -> bool:
    return not (
        that_bbox.xmin > this_bbox.xmin
        or that_bbox.ymin > this_bbox.ymin
        or that_bbox.xmax < this_bbox.xmax
        or that_bbox.ymax < this_bbox.ymax
    )


class RTreeObject:

    __slots__ = ("parent", "xmin", "ymin", "xmax", "ymax", "area")

    def __init__(
        self,
        parent: Optional["RTreeNode"] = None,
        xmin: int = float("inf"),
        ymin: int = float("inf"),
        xmax: int = -float("inf"),
        ymax: int = -float("inf"),
    ) -> None:
        self.parent = parent

        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.area = (self.xmax - self.xmin) * (self.ymax - self.ymin)


class RTreeEntity(RTreeObject):

    __slots__ = ("_id",)

    def __init__(
        self, _id: UID, xmin: int, ymin: int, xmax: int, ymax: int, parent: Optional["RTreeNode"] = None
    ) -> None:
        super().__init__(parent, xmin, ymin, xmax, ymax)
        self._id = _id

    def __repr__(self) -> str:
        return f"RTreeEntity(_id={self._id}, parent={self.parent})"


class RTreeNode(RTreeObject):

    __slots__ = ("height", "is_leaf", "children")

    def __init__(
        self,
        height: int,
        is_leaf: bool,
        children: List[Union["RTreeEntity", "RTreeNode"]],
        parent: Optional["RTreeNode"] = None,
        xmin: int = float("inf"),
        ymin: int = float("inf"),
        xmax: int = -float("inf"),
        ymax: int = -float("inf"),
    ) -> None:
        super().__init__(parent, xmin, ymin, xmax, ymax)
        self.height = height
        self.is_leaf = is_leaf
        self.children = children

        self.update()

    def update(self) -> None:
        xmin = ymin = float("inf")
        xmax = ymax = -float("inf")

        for child in self.children:
            xmin = child.xmin if xmin > child.xmin else xmin
            ymin = child.ymin if ymin > child.ymin else ymin
            xmax = child.xmax if xmax < child.xmax else xmax
            ymax = child.ymax if ymax < child.ymax else ymax

        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.area = (self.xmax - self.xmin) * (self.ymax - self.ymin)

    def __repr__(self) -> str:
        return f"RTreeNode(children_num={len(self.children)}, is_leaf={self.is_leaf}, height={self.height}, parent={self.parent})"


class RTree:
    def __init__(self, max_capacity: int = 9, min_capacity: Optional[int] = None) -> None:
        self.max_capacity = max_capacity
        self.min_capacity = min_capacity if min_capacity != None else int(max_capacity / 2)

        self.entity_index: Dict[UID, RTreeEntity] = {}
        self.root = RTreeNode(children=[], height=0, is_leaf=True)

    def insert(self, entity: BBox) -> None:
        entity_obj = RTreeEntity(
            _id=entity._id,
            xmin=entity.xmin,
            ymin=entity.ymin,
            xmax=entity.xmax,
            ymax=entity.ymax,
        )
        self.entity_index[entity._id] = entity_obj
        self._insert(entity_obj, self.root.height)

    def _insert(self, node_to_insert: Union[RTreeEntity, RTreeNode], height: int) -> None:
        xmin, ymin, xmax, ymax = node_to_insert.xmin, node_to_insert.ymin, node_to_insert.xmax, node_to_insert.ymax
        node = self.choose_subtree(height, xmin, ymin, xmax, ymax)
        node.children.append(node_to_insert)
        node_to_insert.parent = node

        while node:
            if len(node.children) <= self.max_capacity:

                while node:
                    n_xmin, n_ymin, n_xmax, n_ymax = node.xmin, node.ymin, node.xmax, node.ymax
                    node.xmin = xmin if xmin < n_xmin else n_xmin
                    node.ymin = ymin if ymin < n_ymin else n_ymin
                    node.xmax = xmax if xmax > n_xmax else n_xmax
                    node.ymax = ymax if ymax > n_ymax else n_ymax

                    node = node.parent
                break

            self.split(node)
            node = node.parent

    def load(self, entities: List[BBox]) -> None:
        if len(entities) <= self.min_capacity:
            [self.insert(entity) for entity in entities]

        for index, entity in enumerate(entities):
            _id = entity._id
            entity_obj = RTreeEntity(
                _id=_id,
                xmin=entity.xmin,
                ymin=entity.ymin,
                xmax=entity.xmax,
                ymax=entity.ymax,
            )

            self.entity_index[_id] = entity_obj
            entities[index] = entity_obj

        node = self._load(entities)
        root = self.root

        if not self.root.children:
            self.root = node
            return

        root_height = root.height
        node_height = node.height

        if node_height == root_height:
            self.split_root(node)
            return

        if node_height > root_height:
            __temp = root
            self.root = node
            node = __temp

        self._insert(node)

    def _load(self, nodes: List[RTreeEntity | RTreeNode], height: int = 0, is_leaf: bool = True) -> RTreeNode:
        total_nodes = len(nodes)

        if total_nodes <= self.min_capacity:
            root_node = RTreeNode(height=height, is_leaf=is_leaf, parent=None, children=nodes)
            for node in nodes:
                node.parent = root_node
            return root_node

        merged_nodes = []
        self.axis_sort(nodes)
        total_parent_nodes = -(-total_nodes // (self.max_capacity - 1))
        total_partition, total_remainder_node = divmod(total_nodes, total_parent_nodes)
        for i in range(total_parent_nodes):
            node_partition = nodes[
                i * total_partition
                + min(i, total_remainder_node) : (i + 1) * total_partition
                + min(i + 1, total_remainder_node)
            ]
            parent_node = RTreeNode(height=height, is_leaf=is_leaf, parent=None, children=node_partition)
            for node in node_partition:
                node.parent = parent_node
            merged_nodes.append(parent_node)

        return self._load(merged_nodes, height + 1, is_leaf=False)

    def remove(self, _id: UID) -> None:
        try:
            entity_node = self.entity_index[_id]
            del self.entity_index[_id]
        except KeyError as err:
            raise EntityNotFoundError(f"Entity with the id '{_id}' does not exist in RTree") from err

        node = entity_node.parent
        node.children.remove(entity_node)

        entity_to_reallocate: List[RTreeEntity] = []
        while node:
            parent_node = node.parent
            total_children = len(node.children)

            if not parent_node:
                if total_children == 0:
                    self.root = RTreeNode(children=[], height=0, is_leaf=True)
                break

            elif total_children < self.min_capacity:

                if node.is_leaf:
                    entity_to_reallocate.extend(node.children)
                    parent_node.children.remove(node)
                    node.children.clear()

                elif total_children == 0:
                    parent_node.children.remove(node)

            else:
                node.update()

            node = parent_node

        for entity in entity_to_reallocate:
            del self.entity_index[entity._id]
            self.insert(entity)

    def query(self, bbox: BBox) -> List[UID]:
        if not intersect(self.root, bbox):
            return []

        elif within(self.root, bbox):
            return self.get_all_entities(self.root)

        to_process = deque([self.root])
        to_return: List["RTreeNode"] = []

        while to_process:
            node = to_process.pop()
            if not intersect(node, bbox):
                continue

            if node.is_leaf:
                to_return.extend([child._id for child in node.children])

            elif within(node, bbox):
                to_return.extend(self.get_all_entities(node))

            else:
                to_process.extend(node.children)

        return to_return

    def collide(self, bbox: BBox) -> bool:
        if not intersect(self.root, bbox):
            return False

        elif within(self.root, bbox):
            return True

        to_process = deque([self.root])

        while to_process:
            node = to_process.pop()

            if not intersect(node, bbox):
                continue

            if isinstance(node, RTreeEntity) or within(node, bbox):
                return True

            to_process.extend(node.children)

        return False

    def get_all_entities(self, node: RTreeNode) -> List[UID]:
        to_process = deque([node])
        to_return: List[UID] = []
        while to_process:
            node = to_process.pop()
            if node.is_leaf:
                to_return.extend(node.children)
                continue
            to_process.extend(node.children)

        return to_return

    def split(self, old_node: RTreeNode) -> None:
        self.axis_sort(old_node.children)

        old_node_children = old_node.children
        index = self.choose_split_index(old_node_children)
        new_node_children, old_node.children = old_node_children[index:], old_node_children[:index]

        old_node.update()
        new_node = RTreeNode(
            children=new_node_children,
            is_leaf=old_node.is_leaf,
            height=old_node.height,
            parent=old_node.parent,
        )
        for child in new_node_children:
            child.parent = new_node

        if old_node.parent:
            old_node.parent.children.append(new_node)
            return

        self.split_root(new_node)

    def split_root(self, root_sibling: RTreeNode) -> None:
        new_root = RTreeNode(
            children=[self.root, root_sibling],
            height=self.root.height + 1,
            is_leaf=False,
        )
        self.root.parent = root_sibling.parent = new_root
        self.root = new_root

    def choose_split_index(self, nodes: List[RTreeNode]) -> int:
        this_bbox = nodes[0]
        xmin_1, ymin_1, xmax_1, ymax_1 = this_bbox.xmin, this_bbox.ymin, this_bbox.xmax, this_bbox.ymax
        that_bbox = nodes[-1]
        xmin_2, ymin_2, xmax_2, ymax_2 = that_bbox.xmin, that_bbox.ymin, that_bbox.xmax, that_bbox.ymax

        this_node_num = that_node_num = 1
        total_node = self.max_capacity + 1
        for index, bbox in enumerate(nodes[1:-1], 1):

            b_xmin, b_ymin, b_xmax, b_ymax = bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymax

            o_xmin_1, o_ymin_1, o_xmax_1, o_ymax_1 = b_xmin, b_ymin, b_xmax, b_ymax
            o_xmin_2, o_ymin_2, o_xmax_2, o_ymax_2 = b_xmin, b_ymin, b_xmax, b_ymax

            m_xmin_1, m_ymin_1, m_xmax_1, m_ymax_1 = xmin_1, ymin_1, xmax_1, ymax_1
            m_xmin_2, m_ymin_2, m_xmax_2, m_ymax_2 = xmin_2, ymin_2, xmax_2, ymax_2

            if xmin_1 > b_xmin:
                m_xmin_1 = b_xmin
                o_xmin_1 = xmin_1
            if ymin_1 > b_ymin:
                m_ymin_1 = b_ymin
                o_ymin_1 = ymin_1
            if xmax_1 < b_xmax:
                m_xmax_1 = b_xmax
                o_xmax_1 = xmax_1
            if ymax_1 < b_ymax:
                m_ymax_1 = b_ymax
                o_ymax_1 = ymax_1

            dx_1, dy_1 = (o_xmax_1 - o_xmin_1), (o_ymax_1 - o_ymin_1)
            overlapped_area_1 = dx_1 * dy_1 if (dx_1 >= 0) and (dy_1 >= 0) else 0
            merged_area_1 = (m_xmax_1 - m_xmin_1) * (m_ymax_1 - m_ymin_1)

            if xmin_2 > b_xmin:
                m_xmin_2 = b_xmin
                o_xmin_2 = xmin_2
            if ymin_2 > b_ymin:
                m_ymin_2 = b_ymin
                o_ymin_2 = ymin_2
            if xmax_2 < b_xmax:
                m_xmax_2 = b_xmax
                o_xmax_2 = xmax_2
            if ymax_2 < b_ymax:
                m_ymax_2 = b_ymax
                o_ymax_2 = ymax_2

            dx_2, dy_2 = (o_xmax_2 - o_xmin_2), (o_ymax_2 - o_ymin_2)
            overlapped_area_2 = dx_2 * dy_2 if (dx_2 >= 0) and (dy_2 >= 0) else 0
            merged_area_2 = (m_xmax_2 - m_xmin_2) * (m_ymax_2 - m_ymin_2)

            if (total_node - index) <= self.min_capacity:
                if this_node_num < that_node_num:
                    this_node_num += 1
                else:
                    that_node_num += 1

            elif overlapped_area_1 > overlapped_area_2:
                this_node_num += 1

            elif overlapped_area_1 < overlapped_area_2:
                that_node_num += 1

            else:
                if merged_area_1 > merged_area_2:
                    that_node_num += 1
                else:
                    this_node_num += 1

            xmin_2, ymin_2, xmax_2, ymax_2 = m_xmin_2, m_ymin_2, m_xmax_2, m_ymax_2
            xmin_1, ymin_1, xmax_1, ymax_1 = m_xmin_1, m_ymin_1, m_xmax_1, m_ymax_1

        return this_node_num

    def calculate_bbox_distribution(self, bboxes: List[RTreeNode]) -> int:
        first_half_dataset, second_half_dataset = (
            bboxes[: self.min_capacity],
            bboxes[self.min_capacity :],
        )

        margin = 0
        xmin = ymin = float("inf")
        xmax = ymax = -float("inf")
        for bbox in first_half_dataset:
            b_xmin, b_ymin, b_xmax, b_ymax = bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymax
            xmin = b_xmin if b_xmin < xmin else xmin
            ymin = b_ymin if b_ymin < ymin else ymin
            xmax = b_xmax if b_xmax > xmax else xmax
            ymax = b_ymax if b_ymax > ymax else ymax

        margin += (xmax - xmin) + (ymax - ymin)

        for bbox in second_half_dataset:
            b_xmin, b_ymin, b_xmax, b_ymax = bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymax

            xmin = b_xmin if b_xmin < xmin else xmin
            ymin = b_ymin if b_ymin < ymin else ymin
            xmax = b_xmax if b_xmax > xmax else xmax
            ymax = b_ymax if b_ymax > ymax else ymax

            margin += (xmax - xmin) + (ymax - ymin)

        return margin

    def axis_sort(self, bboxes: List[RTreeEntity | RTreeNode]) -> List[RTreeEntity | RTreeNode]:
        """
        assign half of the node's children's bbox to (left // up) TBN, and the that_bbox half to (right // down) TBN
        combine the margin added by the enlargement of the TBN by the that_bbox half of the node's children's bbox
        TBN: temporary bbox node
        """

        # gettting the distribution of the X-axis
        x_margin = 0
        bboxes.sort(key=lambda node: node.xmin)
        x_margin += self.calculate_bbox_distribution(bboxes)
        x_margin += self.calculate_bbox_distribution(bboxes[::-1])

        # gettting the distribution of the Y-axis
        y_margin = 0
        bboxes.sort(key=lambda node: node.ymin)
        y_margin += self.calculate_bbox_distribution(bboxes)
        y_margin += self.calculate_bbox_distribution(bboxes[::-1])

        if y_margin > x_margin:
            bboxes.sort(key=lambda node: node.xmin)

    def choose_subtree(self, height: int, xmin: int, ymin: int, xmax: int, ymax: int) -> RTreeNode:
        depth = 0
        target_node = self.root
        while not target_node.is_leaf and depth != height:
            min_area = min_dead_space = float("inf")

            children = target_node.children
            for child in children:
                c_xmin, c_ymin, c_xmax, c_ymax = child.xmin, child.ymin, child.xmax, child.ymax
                t_xmin = c_xmin if xmin > c_xmin else xmin
                t_ymin = c_ymin if ymin > c_ymin else ymin
                t_xmax = c_xmax if xmax < c_xmax else xmax
                t_ymax = c_ymax if ymax < c_ymax else ymax

                area = child.area
                merged_area = (t_xmax - t_xmin) * (t_ymax - t_ymin)
                dead_space = merged_area - area

                if dead_space < min_dead_space:
                    min_dead_space = dead_space
                    target_node = child

                if area < min_area:
                    min_area = area
                    if dead_space == min_dead_space:
                        target_node = child
            depth += 1

        return target_node
