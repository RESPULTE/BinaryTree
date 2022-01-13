from collections import namedtuple
from typing import List

from .type_hints import Num, Point

BBox = namedtuple("BBox", ["x", "y", "w", "h"], defaults=[1, 1])


def get_dist(p1: Point, p2: Point) -> Num:
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5


def is_intersecting(bbox1: BBox, bbox2: BBox) -> bool:
    return (bbox1.x < bbox2.x + bbox2.w and bbox1.x + bbox1.w > bbox2.x
            and bbox1.y < bbox2.y + bbox2.h and bbox1.y + bbox1.h > bbox2.y)


def split_box(bbox: BBox) -> List[BBox]:
    w, h = bbox.w / 2, bbox.h / 2

    ox, oy = bbox.x, bbox.y

    cx, cy = (bbox.x * 2 + bbox.w) / 2, (bbox.y * 2 + bbox.h) / 2

    return [
        BBox(ox, oy, w, h),
        BBox(cx, oy, w, h),
        BBox(ox, cy, w, h),
        BBox(cx, cy, w, h),
    ]


def is_inscribed(bbox1: BBox, bbox2: BBox) -> float:
    return (bbox2.x <= bbox1.x and bbox2.y <= bbox1.y
            and bbox2.x + bbox2.w >= bbox1.x + bbox1.w
            and bbox2.y + bbox2.h >= bbox1.y + bbox1.h)
