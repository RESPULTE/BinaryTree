from hashlib import new
from typing import List, Tuple

from .kdt_node import KDT_Node
from ..utils import BBox, Point
from ...binarytree._tree import BinaryTree


class KDTree(BinaryTree):

    _node_type = KDT_Node

    def __init__(self, dimension: int = 2):
        super().__init__()
        self.root.dimension = dimension
        self.bbox = BBox(0, 0, 0, 0)

    def insert(self, point: Point) -> None:
        if not isinstance(point, tuple) or \
                any(not isinstance(c, (float, int)) for c in point):
            raise ValueError(f"{type(self).__name__} only accepts tuple of int/float")
        super().insert(point)
        self.bbox.expand(point)

    def delete(self, point: Point) -> None:
        super().delete(point)
        if self.root.value is None:
            self.bbox = BBox(0, 0, 0, 0)
            return

        min_x, min_y, new_w, new_h = self.bbox
        max_x, max_y = min_x + new_w, min_y + new_h

        if point[0] == min_x:
            new_min_x = self.find_min(dimension=0)
            if new_min_x is not None:
                new_w -= new_min_x[0] - min_x
                min_x = new_min_x[0]

        elif point[0] == max_x:
            new_max_x = self.find_max(dimension=0)
            if new_max_x is not None:
                new_w -= max_x - new_max_x[0]

        if point[1] == min_y:
            new_min_y = self.find_min(dimension=1)
            if new_min_y is not None:
                new_h -= new_min_y[1] - min_y
                min_y = new_min_y[1]

        elif point[1] == max_y:
            new_max_y = self.find_max(dimension=1)
            if new_max_y is not None:
                new_h -= max_y - new_max_y[1]

        self.bbox.update(x=min_x, y=min_y, w=new_w, h=new_h)

    def query(self,
              target_point: Point,
              radius: int = 0,
              num: int = 1) -> List[Tuple[Point, float]]:
        found_nodes = self.root.find_closest_node(
            target_point=target_point,
            best_nodes=[],
            num=num
        )

        points_and_dist = [(n.value, abs(d)**0.5) for d, n in found_nodes]

        if radius:
            points_and_dist = [(dist, node) for dist, node in points_and_dist if dist <= radius**2]

        return points_and_dist

    def range(self, x1: int, y1: int, x2: int, y2: int) -> List['KDT_Node']:
        target_bbox = BBox(x1, y1, x2 - x1, y2 - y1)

        if target_bbox.area <= 0:
            raise ValueError('Area must be positive')

        found_nodes: List[KDT_Node] = self.root.find_node_in_bbox(bbox=self.bbox, tbbox=target_bbox)

        return [n.value for n in found_nodes]
