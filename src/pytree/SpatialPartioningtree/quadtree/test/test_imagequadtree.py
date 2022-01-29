import os
import pytest
from pytree import ImageBasedQuadTree, get_super_bbox


@pytest.fixture(scope="session")
def imgquadtree():
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return ImageBasedQuadTree(os.path.join(__location__, 'test_img.jpg'), threshold=10)


def test_compression_completeness(imgquadtree: ImageBasedQuadTree):
    imgquadtree.compress()
    img_bbox = get_super_bbox(*[bbox for _, bbox in imgquadtree.find_leaves()])
    assert (img_bbox.w, img_bbox.h) == imgquadtree.img_size
