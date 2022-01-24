import pytest
from typing import List, Tuple
from pytree import EntityBasedQuadTree


@pytest.fixture
def entityquadtree(
    node_capacity: int = 2,
    auto_id: bool = True,
    max_depth: int = 12,
    max_division: int = 3
):
    return EntityBasedQuadTree(
        bbox=(1000, 1000),
        max_division=max_division,
        max_depth=max_depth,
        node_capacity=node_capacity,
        auto_id=auto_id
    )


@pytest.mark.parametrize('entities', [
    [(100, 100, 10, 10), (90, 90, 20, 20)],
    [(0, 0, 100, 100), (0, 90, 50, 50), (90, 0, 60, 60), (0, 10, 10, 10), (90, 90, 10, 10)]

], ids=['normal', '> node_capacity'])
def test_intersecting_entity_insertion(
    entityquadtree: EntityBasedQuadTree,
    entities: List[Tuple[int, int, int, int]]
):
    for entity in entities:
        entityquadtree.insert(entity)

    for entity_id in entityquadtree.all_entity.keys():
        assert len(entityquadtree.find_entity_node(eid=entity_id)) != 0


@pytest.mark.parametrize('entity', [
    (-10, -10, 10000, 10000), (1500, 1500, 10, 10), (900, 900, 120, 120)
], ids=['too big', 'completely out of bound', 'partially out of bound'])
def test_invalid_entity_insertion(
    entityquadtree: EntityBasedQuadTree,
    entity: Tuple[int, int, int, int]
):
    with pytest.raises(ValueError):
        entityquadtree.insert(entity)


@pytest.mark.parametrize('entities', [
    [(100, 100, 10, 10), (90, 90, 20, 20)],
    [(0, 0, 100, 100), (0, 90, 50, 50), (90, 0, 60, 60), (0, 10, 10, 10)]
], ids=['normal', '> node_capacity'])
def test_entity_node_query(
    entityquadtree: EntityBasedQuadTree,
    entities: List[Tuple[int, int, int, int]]
):
    for entity in entities:
        entityquadtree.insert(entity)

    found_by_id = []
    found_by_bbox = []
    for entity_id, entity_bbox in entityquadtree.all_entity.items():
        found_by_id.append(entityquadtree.find_entity_node(eid=entity_id))
        found_by_bbox.append(entityquadtree.find_entity_node(bbox=entity_bbox))

    for fbi in found_by_id:
        found_by_bbox.remove(fbi)

    assert found_by_bbox == []


@pytest.mark.parametrize('entities, num_intersection', [
    ([(0, 0, 10, 10), (100, 100, 10, 10), (0, 90, 10, 10)], 0),
    ([(100, 100, 10, 10), (90, 90, 20, 20)], 1),
    ([(0, 0, 90, 90), (10, 10, 100, 100), (10, 0, 100, 100), (20, 0, 100, 100)], 3)
], ids=['0 intersection', '1 intersection', '3 intersection'])
def test_entity_query(
    entityquadtree: EntityBasedQuadTree,
    entities: List[Tuple[int, int, int, int]],
    num_intersection: int
):
    for entity in entities:
        entityquadtree.insert(entity)

    for intersected_entity in entityquadtree.query().values():
        assert len(intersected_entity) == num_intersection


@pytest.mark.parametrize('entities', [
    [(100, 100, 10, 10), (90, 90, 20, 20)],
    [(0, 0, 100, 100), (0, 90, 50, 50), (90, 0, 60, 60), (0, 10, 10, 10)]
], ids=['normal', '> node_capacity'])
def test_clean_up(
    entityquadtree: EntityBasedQuadTree,
    entities: List[Tuple[int, int, int, int]]
):
    for entity in entities:
        entityquadtree.insert(entity)

    for entity_id in entityquadtree.all_entity.keys():
        entityquadtree.delete(eid=entity_id)

    entityquadtree.clean_up()

    assert entityquadtree.num_entity_node_in_use == 0
    assert entityquadtree.num_quad_node_in_use == 1


def test_cyclic_reference_in_qnode():
    pass


def test_cyclic_reference_in_entity_node():
    pass


def test_set_branch():
    pass


def test_set_free_qnode():
    pass


def test_find_leaves():
    pass
