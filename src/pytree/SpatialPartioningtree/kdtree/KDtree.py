from typing import List, Tuple

from .kdt_node import KDT_Node
from ..utils import BBox, Point, is_intersecting, is_inscribed, is_within
from ...binarytree._tree import BinaryTree


class KDTree(BinaryTree):

    _node_type = KDT_Node

    def __init__(self, dimension: int = 2):
        super().__init__()
        self.root.dimension = dimension

    @property
    def bbox(self):
        min_x = self.find_min(dimension=0)[0]
        max_x = self.find_max(dimension=0)[0]
        min_y = self.find_min(dimension=1)[1]
        max_y = self.find_max(dimension=1)[1]
        w = max_x - min_x
        h = max_y - min_y

        return BBox(min_x, min_y, w, h)

    # TODO: add radius, num, bbox as the parameter
    def query(self, target_point: Point) -> List[Point]:
        return self.root.find_closest_node(target_point)

    def find_max(self, dimension: int = 1) -> Point:
        return self.root.find_max_node(dimension).value

    def find_min(self, dimension: int = 1) -> Point:
        return self.root.find_min_node(dimension).value

    def find_lt(self, target_point: Point, dimension: int = 1) -> Point:
        return self.root.find_lt_node(target_point, dimension).value

    def find_le(self, target_point: Point, dimension: int = 1) -> Point:
        return self.root.find_le_node(target_point, dimension).value

    def find_gt(self, target_point: Point, dimension: int = 1) -> Point:
        return self.root.find_gt_node(target_point, dimension).value

    def find_ge(self, target_point: Point, dimension: int = 1) -> Point:
        return self.root.find_ge_node(target_point, dimension).value

    def range(self, target_area: Tuple[int, int, int, int]) -> List['KDT_Node']:
        try:
            x1, y1, x2, y2 = target_area
        except ValueError:
            raise ValueError('Target area must be a tuple of 4 integers')
        target_bbox = BBox(x1, y1, x2 - x1, y2 - y1)

        def traversal_inspector(
            bbox: BBox,
            node: 'KDT_Node',
            depth: int = 0
        ):
            cd = depth % self.root.dimension

            if is_inscribed(bbox, target_bbox):
                return node.traverse_node(node=False)

            x, y, w, h = bbox
            if cd == 0:
                left_bbox = BBox(x, y, w - node.value[0], h)
                right_bbox = BBox(x + node.value[0], y, w, h)
            else:
                left_bbox = BBox(x, y, w, h - node.value[1])
                right_bbox = BBox(x, y + node.value[1], w, h)

            bounded_points = []

            if is_intersecting(left_bbox, target_bbox):
                if node.left:
                    bounded_points.extend(traversal_inspector(left_bbox, node.left, depth + 1))

            if is_intersecting(right_bbox, target_bbox):
                if node.right:
                    bounded_points.extend(traversal_inspector(right_bbox, node.right, depth + 1))

            if is_within(node.value, target_bbox) and node.value not in bounded_points:
                bounded_points.append(node.value)

            return bounded_points

        return traversal_inspector(self.bbox, self.root)
