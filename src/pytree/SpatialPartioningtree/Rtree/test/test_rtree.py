import pytest
from random import randint as rnd
from pytree import RTree
from pytree.SpatialPartioningtree.Rtree import get_children


@pytest.fixture
def rtree():
    return RTree(auto_id=True)


@pytest.fixture
def entities():
    return [tuple([rnd(0, 1000) for _ in range(4)]) for _ in range(0, 1000)]


@pytest.fixture
def filled_rtree(entities):
    return RTree.fill_tree(entities, auto_id=True)


def test_insertion(filled_rtree: RTree, entities):
    assert filled_rtree.height >= 1

    num_inserted_entities = 0
    for leaf in filled_rtree.find_leaves():
        assert leaf.is_leaf
        num_inserted_entities += len(get_children(leaf))

    assert len(entities) == num_inserted_entities


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
