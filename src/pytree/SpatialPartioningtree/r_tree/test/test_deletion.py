from textwrap import fill
import pytest
from pytree import RTree
from pytree.SpatialPartioningtree.r_tree._r_node import get_children


@pytest.fixture
def rtree():
    return RTree(auto_id=True)


@pytest.fixture
def entities():
    return [
        (10, 10, 20, 20), (0, 0, 20, 20), (1000, 100, 20, 20),
        (900, 500, 20, 20), (34, 45, 1, 1), (34, 4534, 1, 1),
        (34, 45, 10, 10), (34, 45, 1670, 10), (12, 23, 545, 56),
        (23, 45, 24, 56), (234, 231, 56, 23), (0, 34, 2, 1)
    ]


@pytest.fixture
def filled_rtree(entities):
    return RTree.fill_tree(entities, auto_id=True)


def test_insertion(filled_rtree: RTree, entities):
    assert filled_rtree.height >= 1

    inserted_entities = []
    for leaf in filled_rtree.find_leaves():
        assert leaf.is_leaf
        inserted_entities.extend(get_children(leaf))

    assert len(entities) == len(inserted_entities)


def test_invalid_id_deletion(filled_rtree: RTree):
    with pytest.raises(ValueError):
        filled_rtree.delete('najib')


def test_delete_from_underflowing_node(filled_rtree):
    pass


def test_get_bounding_leaf(filled_rtree):
    pass


def test_invalid_data_insertion(rtree):
    pass


def test_invalid_data_deletion(rtree):
    pass


def test_query(filled_rtree):
    pass
