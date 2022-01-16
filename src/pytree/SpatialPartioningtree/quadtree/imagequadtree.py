from typing import Optional, Tuple
from PIL import Image, ImageDraw
import numpy as np

from ..utils import BBox, split_box, crop_img, get_average_rgb
from ._quadtree import QuadNode, QuadTree


class ImageBasedQuadTree(QuadTree):

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

        self.compressed = False

        super().__init__(img_to_process.size, max_depth)

    def compress(self) -> Image.Image:

        def recursive_compress(qnode: QuadNode,
                               qindex: int,
                               bbox: BBox,
                               depth: int = 0):

            img = crop_img(self.img_arr, bbox)
            avg_color, error = get_average_rgb(img)

            if error <= self.threshold or \
                bbox.w <= 1 or bbox.h <= 1 \
                    or depth > self.max_depth:

                qnode.update(first_child=avg_color, total_entity=1)
                return

            self.set_branch(qnode, qindex)

            for ind, quadrant in enumerate(split_box(bbox, True)):
                child_index = qnode.first_child + ind
                recursive_compress(self.all_quad_node[child_index],
                                   child_index, quadrant, depth + 1)

        if self.compressed:
            return
        recursive_compress(self.root, 0, self.bbox)
        self.compressed = True

    def draw(self,
             outline: Optional[Tuple[int, int, int]] = None) -> Image.Image:
        if not self.compressed:
            raise Exception("image hasn't been compressed")

        self.img = Image.new("RGB", self.img_size, (255, 255, 255))

        draw = ImageDraw.Draw(self.img)

        for leaf, bbox in self.find_leaves(qnode=self.root):
            x, y, w, h = bbox
            draw.rectangle((x, y, x + w, y + h),
                           fill=leaf.first_child,
                           outline=outline)

    def save(self,
             filename: Optional[str] = None,
             format: Optional[str] = 'png') -> None:
        if not self.compressed:
            raise Exception("image hasn't been compressed")
        if not filename:
            filename = self.img_name
        self.img.save(f"{filename}.{format}")

    def show(self):
        self.img.show(title=self.img_name)
