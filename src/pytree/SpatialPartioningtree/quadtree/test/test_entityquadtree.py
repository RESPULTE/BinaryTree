import pytest
from typing import List, Tuple
from pytree import EntityBasedQuadTree, QuadEntityNode, BBox


@pytest.fixture
def entityquadtree():
    return EntityBasedQuadTree(bbox=(1000, 1000), auto_id=True)


@pytest.mark.dependency()
def test_set_branch(entityquadtree: EntityBasedQuadTree):
    root = entityquadtree.root
    entityquadtree.set_branch(root, 0)
    tree_size = entityquadtree.num_quad_node
    for i in range(4):
        assert root.first_child + i < tree_size

        child = entityquadtree.all_quad_node[root.first_child + i]
        assert child.parent_index == 0
        assert child.is_leaf

    assert (root.first_child - 1) % 4 == 0
    assert root.is_branch


@pytest.mark.dependency()
def test_add_entity_node(entityquadtree: EntityBasedQuadTree):
    all_entity_node = entityquadtree.all_entity_node
    root = entityquadtree.root
    entityquadtree.add_entity_node(root, 10)
    entityquadtree.add_entity_node(root, 11)

    first_child = all_entity_node[root.first_child]
    second_child = all_entity_node[first_child.next_index]

    assert isinstance(first_child, QuadEntityNode)
    assert isinstance(second_child, QuadEntityNode)

    assert first_child.owner_node == root
    assert second_child.owner_node == root

    assert first_child.entity_id == 11
    assert second_child.entity_id == 10


@pytest.mark.dependency(depends=["test_set_branch"])
def test_free_qnode_utilization(entityquadtree: EntityBasedQuadTree):
    entityquadtree.set_branch(entityquadtree.root, 0)

    first_child_index = entityquadtree.root.first_child
    entityquadtree.set_branch(entityquadtree.all_quad_node[first_child_index], first_child_index)

    entityquadtree.set_free_quad_node(first_child_index)

    for bbox in [(0, 0, 10, 10), (0, 90, 50, 50), (900, 0, 60, 60), (0, 100, 10, 10)]:
        entityquadtree.insert(bbox)

    assert entityquadtree._free_quad_node_index == -1


@pytest.mark.dependency(depends=["test_set_branch"])
def test_find_leaves(entityquadtree: EntityBasedQuadTree):
    root = entityquadtree.root
    all_qnode = entityquadtree.all_quad_node

    entityquadtree.set_branch(root, 0)
    entityquadtree.set_branch(all_qnode[root.first_child], 1)
    entityquadtree.set_branch(all_qnode[root.first_child + 1], 2)

    assert len(entityquadtree.find_leaves(qnode=entityquadtree.root)) == 10
    assert len(entityquadtree.find_leaves(bbox=entityquadtree.bbox)) == 10


@pytest.mark.dependency(depends=["test_set_branch", "test_add_entity_node"])
def test_find_entity_node(entityquadtree: EntityBasedQuadTree):
    root = entityquadtree.root
    all_qnode = entityquadtree.all_quad_node

    entityquadtree.set_branch(root, 0)
    entityquadtree.set_branch(all_qnode[root.first_child], 1)
    entityquadtree.set_branch(all_qnode[all_qnode[root.first_child].first_child], 5)

    target_child = all_qnode[all_qnode[root.first_child].first_child]
    entityquadtree.all_entity[1] = BBox(1, 1, 1, 1)
    entityquadtree.add_entity_node(target_child, 1)

    found_entity_node = entityquadtree.find_entity_node(qnode=target_child)
    assert found_entity_node[0].entity_id == 1

    found_entity_node = entityquadtree.find_entity_node(eid=1)
    assert found_entity_node[0].entity_id == 1

    found_entity_node = entityquadtree.find_entity_node(bbox=entityquadtree.bbox)
    assert found_entity_node[0].entity_id == 1


@pytest.mark.dependency(depends=["test_find_entity_node"])
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


@pytest.mark.dependency(depends=["test_find_entity_node"])
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


@pytest.mark.dependency(depends=["test_set_branch"])
def test_tree_height(entityquadtree: EntityBasedQuadTree):
    all_qnode = entityquadtree.all_quad_node

    entityquadtree.set_branch(entityquadtree.root, 0)
    qnode, qindex, height = all_qnode[1], 1, 1

    while height < 10:
        entityquadtree.set_branch(qnode, qindex)
        qnode = all_qnode[qnode.first_child]
        qindex += 4
        height += 1

    assert entityquadtree.depth == height


@pytest.mark.dependency(depends=["test_intersecting_entity_insertion"])
def test_max_depth_stopper(entityquadtree: EntityBasedQuadTree):
    entityquadtree.max_division = 5
    entityquadtree.max_depth = 10
    entityquadtree.node_capacity = 1
    entityquadtree.insert((0, 0, 101, 100))
    entityquadtree.insert((0, 0, 100, 100))
    assert entityquadtree.max_depth == 10
