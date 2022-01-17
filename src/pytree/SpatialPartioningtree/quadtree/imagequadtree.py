from PIL import Image, ImageDraw
from typing import Optional
import numpy as np

from ..type_hints import RGB
from ..utils import BBox, split_box, crop_img_arr, get_average_rgb

from ._quadtree import QuadTree
from ._quadnode import QuadNode


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

        super().__init__(img_to_process.size, max_depth)

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

            self.set_branch(qnode, qindex)

            for ind, quadrant in enumerate(split_box(bbox, True)):
                child_index = qnode.first_child + ind
                recursive_compress(self.all_quad_node[child_index],
                                   child_index, quadrant, num_division + 1)

        if self.img:
            return
        recursive_compress(self.root, 0, self.bbox)

    def draw(self, outline: Optional[RGB] = None) -> Image.Image:
        self.img = Image.new("RGB", self.img_size)

        draw = ImageDraw.Draw(self.img)

        for leaf, bbox in self.find_leaves(qnode=self.root):
            x, y, w, h = bbox
            draw.rectangle((x, y, x + w, y + h),
                           fill=leaf.first_child,
                           outline=outline)

    def save(self,
             filename: Optional[str] = None,
             format: Optional[str] = 'png') -> None:
        if not self.img:
            raise Exception("image hasn't been compressed")
        if not filename:
            filename = self.img_name
        self.img.save(f"{filename}.{format}")

    def show(self):
        self.img.show()
