from typing import List, Optional, Tuple

from pytree.SpatialPartioningtree.type_hints import Num, Point, UID


class BBox:

    __slots__ = ["x", "y", "w", "h"]

    def __init__(self, x: int, y: int, w: int = 1, h: int = 1):
        if not all(isinstance(pos, (int, float)) for pos in [x, y, w, h]):
            raise ValueError("bbox of entity should be of type 'int'")

        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def uninitialised(self):
        return self.area == 0

    @property
    def area(self) -> float:
        return self.w * self.h

    @property
    def midpoint(self) -> Point:
        return (self.x + self.w) / 2, (self.y + self.h) / 2

    @property
    def corner(self) -> Tuple[Point, Point, Point, Point]:
        if self.area == 0:
            return ((self.x, self.y),)

        return (
            (self.x, self.y),  # topleft
            (self.x + self.w, self.y),  # topright
            (self.x, self.y + self.h),  # bottomleft
            (self.x + self.w, self.y + self.h),  # bottomright
        )

    @classmethod
    def get_bbox(cls, *points: Point) -> "BBox":
        points = list(points)

        x_sorted = sorted(points, key=lambda p: p[0])
        y_sorted = sorted(points, key=lambda p: p[1])

        x = x_sorted[0][0]
        y = y_sorted[0][1]

        new_w = x_sorted[-1][0] - x
        new_h = y_sorted[-1][1] - y

        return cls(x, y, new_w, new_h)

    @classmethod
    def get_super_bbox(cls, *bbox: "BBox") -> "BBox":
        x = min(bbox, key=lambda b: b.x).x
        y = min(bbox, key=lambda b: b.y).y

        max_x = max(bbox, key=lambda b: b.x + b.w)
        new_w = (max_x.x + max_x.w) - x

        max_y = max(bbox, key=lambda b: b.y + b.h)
        new_h = (max_y.y + max_y.h) - y

        return cls(x, y, new_w, new_h)

    def copy(self) -> "BBox":
        return BBox(self.x, self.y, self.w, self.h)

    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]

    def trim_ip(self, other: "BBox") -> None:
        px1, py1, px2, py2 = self.x, self.y, self.x + self.w, self.y + self.h
        ox1, oy1, ox2, oy2 = other.x, other.y, other.x + other.w, other.y + other.h

        x1, x2 = max(px1, ox1), min(ox2, px2)
        y1, y2 = max(py1, oy1), min(py2, oy2)
        w, h = x2 - x1, y2 - y1

        self.update(x=x1, y=y1, w=w, h=h)

    def trim(self, other: "BBox") -> "BBox":
        px1, py1, px2, py2 = self.x, self.y, self.x + self.w, self.y + self.h
        ox1, oy1, ox2, oy2 = other.x, other.y, other.x + other.w, other.y + other.h

        x1, x2 = max(px1, ox1), min(ox2, px2)
        y1, y2 = max(py1, oy1), min(py2, oy2)
        w, h = x2 - x1, y2 - y1

        return BBox(x=x1, y=y1, w=w, h=h)

    def split(self, roundoff: Optional[bool] = False) -> List["BBox"]:
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

    def is_within(self, other: "BBox") -> float:
        return (
            other.x <= self.x
            and other.y <= self.y
            and other.x + other.w >= self.x + self.w
            and other.y + other.h >= self.y + self.h
        )

    def intersect(self, other: "BBox") -> bool:
        return (
            self.x < other.x + other.w
            and self.x + self.w > other.x
            and self.y < other.y + other.h
            and self.y + self.h > other.y
        )

    def enclose(self, point: Point) -> bool:
        return self.x + self.w >= point[0] >= self.x and self.y + self.h >= point[1] >= self.y

    def expand(self, point: Point) -> "BBox":
        if self.area == 0 and self.x == 0 and self.y == 0:
            return BBox(*point, 0, 0)
        return BBox.get_bbox(*self.corner, point)

    def expand_ip(self, point: Point) -> None:
        if self.area == 0 and self.x == 0 and self.y == 0:
            self.update(x=point[0], y=point[1])
            return

        expanded_bbox = BBox.get_bbox(*self.corner, point)
        if expanded_bbox.area > self.area:
            x, y, w, h = expanded_bbox
            self.update(x=x, y=y, w=w, h=h)

    def __eq__(self, other: "BBox") -> bool:
        return self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h

    def __ne__(self, other: "BBox") -> bool:
        return self.x != other.x or self.y != other.y or self.w != other.w or self.h != other.h

    def __gt__(self, other: "BBox") -> bool:
        return self.area > other.area

    def __lt__(self, other: "BBox") -> bool:
        return self.area < other.area

    def __ge__(self, other: "BBox") -> bool:
        return self.area >= other.area

    def __le__(self, other: "BBox") -> bool:
        return self.area <= other.area

    def __hash__(self):
        return hash(self.x, self.y, self.w, self.h)

    def __iter__(self):
        return iter([self.x, self.y, self.w, self.h])


def get_squared_distance(this_point: Point, that_point: Point) -> float:
    this_dimension = len(this_point)
    that_dimension = len(that_point)
    if this_dimension != that_dimension:
        raise ValueError("inconsistent dimension of points")
    if this_dimension < 2 or that_dimension < 2:
        raise ValueError("1 dimensional data points are not supported")

    return sum((p1 - p2) ** 2 for p1, p2 in zip(this_point, that_point))


def get_closest(this_point: Point, that_point: Point, target_point: Point) -> Tuple[Num, Point]:
    this_node_dist = get_squared_distance(this_point, target_point)
    that_node_dist = get_squared_distance(that_point, target_point)

    if this_node_dist < that_node_dist:

        return this_node_dist, this_point

    return that_node_dist, that_point


def within_radius(origin_point: Point, radius: float, bbox: BBox) -> bool:
    dist = radius ** 2
    for c in bbox.corner:
        if get_squared_distance(c, origin_point) <= dist:
            return True

    return False


def generate_id(id_catalogue: List[UID]) -> UID:
    int_id = list(filter(lambda id: isinstance(id, (int, float)), id_catalogue))
    if not int_id:
        int_id.append(0)
    return max(int_id) + 1
