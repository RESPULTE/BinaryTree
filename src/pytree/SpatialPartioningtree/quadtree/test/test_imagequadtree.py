import pytest
from pytree import ImageBasedQuadTree, get_super_bbox


@pytest.fixture(scope="session")
def imgquadtree():
    return ImageBasedQuadTree(
        "C:/Users/yeapz/OneDrive/Desktop/Python/PyTree/src/pytree/kest.jpg",
        threshold=10)


def test_compression_completeness(imgquadtree: ImageBasedQuadTree):
    imgquadtree.compress()

    img_bbox = get_super_bbox(*[bbox for _, bbox in imgquadtree.find_leaves()])

    assert (img_bbox.w, img_bbox.h) == imgquadtree.img_size
