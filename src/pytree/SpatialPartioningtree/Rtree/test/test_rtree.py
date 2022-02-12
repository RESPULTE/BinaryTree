import pytest
from random import randint as rnd
from pytree import RTree, BBox
from pytree.SpatialPartioningtree.Rtree.rtree import get_children


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
    for leaf in filled_rtree._find_leaves():
        assert leaf.is_leaf
        num_inserted_entities += len(get_children(leaf))

    assert len(entities) == num_inserted_entities


def test_invalid_id_deletion(filled_rtree: RTree):
    with pytest.raises(ValueError):
        filled_rtree.delete('najib')


def test_find_rnode(rtree: RTree):
    rtree.insert((0, 0, 10, 10))
    rtree.insert((10, 10, 1, 1))
    rtree.insert((14, 12, 11, 79))
    rtree.insert((90, 90, 10, 10))

    assert rtree._find_rnode(BBox(0, 0, 100, 100)) == rtree.root


def test_invalid_data_deletion(filled_rtree):
    with pytest.raises(ValueError):
        filled_rtree.delete('120')


@pytest.mark.parametrize('entities, target_area, num_entity', [
    ([(100, 100, 10, 10), (90, 90, 20, 20)], (900, 900, 1, 1), 0),
    ([(0, 0, 10, 10), (100, 100, 10, 10), (0, 90, 10, 10)], (0, 0, 20, 95), 2),
    ([(0, 0, 90, 90), (10, 10, 100, 100), (10, 0, 100, 100), (20, 0, 100, 100)], (0, 0, 900, 900), 4)
], ids=['2 entity', '0 entity', '4 entity'])
def test_query_entity_with_bbox(
    rtree: RTree,
    entities: list,
    target_area: tuple,
    num_entity: int
):
    for entity in entities:
        rtree.insert(entity)
    assert len(rtree.query_entity(bbox=target_area)) == num_entity


@pytest.mark.parametrize('entities, point_n_radius, num_entity', [
    ([(0, 0, 10, 10), (100, 100, 10, 10), (0, 90, 10, 10)], ((0, 0), 150), 3),
    ([(100, 100, 10, 10), (90, 90, 20, 20)], ((900, 900), 2), 0),
    ([(0, 0, 90, 90), (10, 10, 100, 100), (100, 200, 100, 100), (200, 700, 100, 100)], ((0, 0), 20), 2)
], ids=['2 entity', '0 entity', '4 entity'])
def test_query_entity_with_circle(
    rtree: RTree,
    entities: list,
    point_n_radius: tuple,
    num_entity: int
):
    for entity in entities:
        rtree.insert(entity)
    assert len(rtree.query_entity(radius=point_n_radius)) == num_entity
