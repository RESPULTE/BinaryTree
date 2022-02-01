from collections import namedtuple
from typing import List, Optional, Tuple

from .type_hints import Num, Point

BBox = namedtuple("BBox", ["x", "y", "w", "h"], defaults=[1, 1])


def get_squared_distance(this_point: Point, that_point: Point) -> float:
    return sum((p1 - p2)**2 for p1, p2 in zip(this_point, that_point))


def get_closest(this_point: Point, that_point: Point,
                target_point: Point) -> Tuple[Num, Point]:
    this_node_dist = get_squared_distance(this_point, target_point)
    that_node_dist = get_squared_distance(that_point, target_point)

    if this_node_dist < that_node_dist:

        return this_node_dist, this_point

    return that_node_dist, that_point


def is_intersecting(bbox1: BBox, bbox2: BBox) -> bool:
    return (bbox1.x < bbox2.x + bbox2.w and
            bbox1.x + bbox1.w > bbox2.x and
            bbox1.y < bbox2.y + bbox2.h and
            bbox1.y + bbox1.h > bbox2.y)


def split_box(bbox: BBox, whole_num: Optional[bool] = False) -> List[BBox]:
    w, h = bbox.w / 2, bbox.h / 2

    ox, oy = bbox.x, bbox.y

    cx, cy = (bbox.x * 2 + bbox.w) / 2, (bbox.y * 2 + bbox.h) / 2
    if whole_num:
        w, h = int(w), int(h)
        ox, oy, cx, cy = int(ox), int(oy), int(cx), int(cy)

    return [
        BBox(ox, oy, w, h),
        BBox(cx, oy, w, h),
        BBox(ox, cy, w, h),
        BBox(cx, cy, w, h),
    ]


def is_inscribed(bbox1: BBox, tbbox2: BBox) -> float:
    return (tbbox2.x <= bbox1.x and
            tbbox2.y <= bbox1.y and
            tbbox2.x + tbbox2.w >= bbox1.x + bbox1.w and
            tbbox2.y + tbbox2.h >= bbox1.y + bbox1.h)


def is_within(point: Point, bbox: BBox) -> bool:
    return (bbox.x + bbox.w >= point[0] >= bbox.x and bbox.y + bbox.h >= point[1] >= bbox.y)


def get_super_bbox(*bbox: BBox) -> BBox:
    x = min(bbox, key=lambda b: b.x).x
    y = min(bbox, key=lambda b: b.y).y

    max_x = max(bbox, key=lambda b: b.x + b.w)
    width = (max_x.x + max_x.w) - x
    max_y = max(bbox, key=lambda b: b.y + b.h)
    height = (max_y.y + max_y.h) - y

    return BBox(x, y, width, height)


def get_area(bbox: BBox) -> float:
    return bbox.w * bbox.h


def get_bounding_area(*bbox: BBox) -> float:
    return get_area(get_super_bbox(*bbox))


def get_bbox(*points: Point) -> BBox:
    points = list(points)

    x_sorted = sorted(points, key=lambda p: p[0])
    y_sorted = sorted(points, key=lambda p: p[1])

    x = x_sorted[0][0]
    y = y_sorted[0][1]

    width = x_sorted[-1][0] - x
    height = y_sorted[-1][1] - y

    return BBox(x, y, width, height)


def expand_bbox(bbox: BBox, point: Point) -> BBox:
    if bbox.w == 0 and bbox.h == 0:
        if bbox.x == 0 and bbox.y == 0:
            return BBox(x=point[0], y=point[1], w=0, h=0)
        return get_bbox((bbox.x, bbox.y), point)

    min_x, min_y, width, height = bbox
    max_x, max_y = min_x + width, min_y + height

    if point[0] < min_x:
        min_x = point[0]

    elif point[0] > max_x:
        width = point[0] - min_x

    if point[1] < min_y:
        min_y = point[1]

    elif point[1] > max_y:
        height = point[1] - min_y

    return bbox._replace(x=min_x, y=min_y, w=width, h=height)
