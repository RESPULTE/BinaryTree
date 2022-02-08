from typing import List, Optional, Tuple

from .type_hints import Num, Point, UID


class BBox:

    __slots__ = ['x', 'y', 'w', 'h']

    def __init__(self, x: int, y: int, w: int = 1, h: int = 1):
        if not all(isinstance(pos, (int, float)) for pos in [x, y, w, h]):
            raise ValueError("bbox of entity should be of type 'int'")

        if w * h < 0:
            raise ValueError("main bounding box must have a non-negative area")

        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def area(self) -> float:
        return self.w * self.h

    @classmethod
    def get_bbox(cls, *points: Point) -> 'BBox':
        points = list(points)

        x_sorted = sorted(points, key=lambda p: p[0])
        y_sorted = sorted(points, key=lambda p: p[1])

        x = x_sorted[0][0]
        y = y_sorted[0][1]

        width = x_sorted[-1][0] - x
        height = y_sorted[-1][1] - y

        return cls(x, y, width, height)

    @classmethod
    def get_super_bbox(cls, *bbox: 'BBox') -> 'BBox':
        x = min(bbox, key=lambda b: b.x).x
        y = min(bbox, key=lambda b: b.y).y

        max_x = max(bbox, key=lambda b: b.x + b.w)
        width = (max_x.x + max_x.w) - x

        max_y = max(bbox, key=lambda b: b.y + b.h)
        height = (max_y.y + max_y.h) - y

        return cls(x, y, width, height)

    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]

    def split(self, roundoff: Optional[bool] = False) -> List['BBox']:
        w, h = self.w / 2, self.h / 2

        ox, oy = self.x, self.y

        cx, cy = (self.x * 2 + self.w) / 2, (self.y * 2 + self.h) / 2
        if roundoff:
            w, h = int(w), int(h)
            ox, oy, cx, cy = int(ox), int(oy), int(cx), int(cy)

        return [
            type(self)(ox, oy, w, h),
            type(self)(cx, oy, w, h),
            type(self)(ox, cy, w, h),
            type(self)(cx, cy, w, h),
        ]

    def is_within(self, other: 'BBox') -> float:
        return (other.x <= self.x and
                other.y <= self.y and
                other.x + other.w >= self.x + self.w and
                other.y + other.h >= self.y + self.h)

    def intersect(self, other: 'BBox') -> bool:
        return (self.x < other.x + other.w and
                self.x + self.w > other.x and
                self.y < other.y + other.h and
                self.y + self.h > other.y)

    def enclose(self, point: Point) -> bool:
        return (self.x + self.w >= point[0] >= self.x and self.y + self.h >= point[1] >= self.y)

    def expand(self, point: Point) -> None:
        min_x, min_y, width, height = 0, 0, 0, 0

        if self.w == 0 and self.h == 0:
            if self.x == 0 and self.y == 0:
                min_x, min_y = point[0], point[1]
            else:
                bbox = BBox.get_bbox((self.x, self.y), point)
                min_x, min_y, width, height = bbox
        else:
            min_x, min_y, width, height = self
            max_x, max_y = min_x + width, min_y + height

            if point[0] < min_x:
                min_x = point[0]

            elif point[0] > max_x:
                width = point[0] - min_x

            if point[1] < min_y:
                min_y = point[1]

            elif point[1] > max_y:
                height = point[1] - min_y

        return self.update(x=min_x, y=min_y, w=width, h=height)

    def __hash__(self):
        return hash(self.x, self.y, self.w, self.h)

    def __iter__(self):
        return iter([self.x, self.y, self.w, self.h])


def get_squared_distance(this_point: Point, that_point: Point) -> float:
    return sum((p1 - p2)**2 for p1, p2 in zip(this_point, that_point))


def get_closest(this_point: Point, that_point: Point,
                target_point: Point) -> Tuple[Num, Point]:
    this_node_dist = get_squared_distance(this_point, target_point)
    that_node_dist = get_squared_distance(that_point, target_point)

    if this_node_dist < that_node_dist:

        return this_node_dist, this_point

    return that_node_dist, that_point


def generate_id(id_catalogue: List[UID]) -> UID:
    int_id = list(filter(lambda id: isinstance(id, (int, float)), id_catalogue))
    if not int_id:
        int_id.append(0)
    return max(int_id) + 1
