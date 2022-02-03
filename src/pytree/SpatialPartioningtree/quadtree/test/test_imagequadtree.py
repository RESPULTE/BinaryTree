import os
import pytest
from pytree import ImageBasedQuadTree


@pytest.fixture(scope="session")
def imgquadtree():
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return ImageBasedQuadTree(os.path.join(__location__, 'test_img.jpg'), threshold=30)


@pytest.mark.skip(reason="it takes too goddamn long")
def test_compression_completeness(imgquadtree: ImageBasedQuadTree):
    imgquadtree.compress()
    total_img_area = imgquadtree.img_size[0] * imgquadtree.img_size[1]
    sum_all_bbox_area = sum(bbox.w * bbox.h for _, bbox in imgquadtree.find_leaves())

    assert sum_all_bbox_area == total_img_area
