from collections import namedtuple
from typing import List, Optional, Tuple
import numpy as np

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
    return (bbox1.x < bbox2.x + bbox2.w and bbox1.x + bbox1.w > bbox2.x
            and bbox1.y < bbox2.y + bbox2.h and bbox1.y + bbox1.h > bbox2.y)


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


def is_inscribed(bbox1: BBox, bbox2: BBox) -> float:
    return (bbox2.x <= bbox1.x and bbox2.y <= bbox1.y
            and bbox2.x + bbox2.w >= bbox1.x + bbox1.w
            and bbox2.y + bbox2.h >= bbox1.y + bbox1.h)


def crop_img(img_arr: np.array, bbox: BBox) -> np.array:
    x, y, w, h = bbox
    return img_arr[y:y + h, x:x + w]


def calculate_avg_std(
        rgb_channel: np.ndarray) -> Tuple[Tuple[int, int, int], float]:
    rgb = np.reshape(rgb_channel, -1)
    avg = np.mean(rgb)
    std = np.std(rgb)
    return int(avg), std


def get_average_rgb(img_arr: np.ndarray) -> Tuple[Tuple[int, int, int], float]:
    r, re = calculate_avg_std(img_arr[:, :, 0])
    g, ge = calculate_avg_std(img_arr[:, :, 1])
    b, be = calculate_avg_std(img_arr[:, :, 2])
    e = re * 0.299 + 0.587 * ge + 0.114 * be
    return (r, g, b), e
