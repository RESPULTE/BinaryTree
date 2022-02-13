from PIL import Image, ImageDraw
from typing import Optional, Tuple
import numpy as np
import os

from pytree.SpatialPartioningtree.Quadtree.basequadtree import BaseQuadTree, QuadNode
from pytree.SpatialPartioningtree.type_hints import RGB
from pytree.SpatialPartioningtree.utils import BBox


def get_average_rgb(img_arr: np.ndarray) -> Tuple[RGB, float]:
    r, g, b = [int(num) for num in np.mean(img_arr, axis=(0, 1))]
    re, ge, be = np.std(img_arr, axis=(0, 1))
    e = 0.299 * re + 0.587 * ge + 0.114 * be
    return (r, g, b), e


def crop_img_arr(img_arr: np.ndarray, bbox: BBox) -> np.ndarray:
    x, y, w, h = bbox
    return img_arr[y:y + h, x:x + w]


class ImageBasedQuadTree(BaseQuadTree):

    def __init__(self,
                 img_dir: str,
                 max_depth: int = 7,
                 threshold: int = 1) -> None:

        img_to_process = Image.open(img_dir)

        self.img = None
        self.img_name = f"{img_dir.split('/')[-1].split('.')[0]}_compressed"
        self.img_size = img_to_process.size
        self.img_arr = np.asarray(img_to_process, dtype="int32")
        self.threshold = threshold

        super().__init__(size=img_to_process.size, max_depth=max_depth)

    def compress(self) -> Image.Image:

        def recursive_compress(qnode: QuadNode,
                               qindex: int,
                               bbox: BBox,
                               num_division: int = 0):

            img = crop_img_arr(self.img_arr, bbox)
            avg_color, error = get_average_rgb(img)

            if error <= self.threshold or \
                bbox.w <= 1 or bbox.h <= 1 \
                    or num_division > self.max_depth:

                qnode.update(first_child=avg_color, total_entity=1)
                return

            self._set_branch(qnode, qindex)

            for ind, quadrant in enumerate(bbox.split(roundoff=True)):
                child_index = qnode.first_child + ind
                recursive_compress(self.all_quad_node[child_index],
                                   child_index, quadrant, num_division + 1)

        if self.img:
            return
        recursive_compress(self.root, 0, self.bbox)

    def draw(self, outline: Optional[RGB] = None) -> Image.Image:
        self.img = Image.new("RGB", self.img_size)

        draw = ImageDraw.Draw(self.img)

        for leaf, bbox in self._find_leaves():
            x, y, w, h = bbox
            draw.rectangle((x, y, x + w, y + h),
                           fill=leaf.first_child,
                           outline=outline)

    def save(self,
             filepath: Optional[str] = None,
             format: Optional[str] = 'png') -> None:
        if not self.img:
            raise Exception("image hasn't been compressed")
        if not filepath:
            filepath = self.img_name

        self.img.save(f"{os.path.join(*filepath.split('/'))}.{format}")

    def show(self):
        if self.img is None:
            raise ValueError("No image to display")
        self.img.show()

    def __bool__(self):
        return self.img is not None

    def __iter__(self):
        yield from [(e.first_child, bbox) for e, bbox in self._find_leaves()]

    def __str__(self):
        return f"{type(self).__name__}( \
            img_name={self.img_name}, \
            img_size={self.img_size}, \
            threshold={self.threshold} \
        )"
