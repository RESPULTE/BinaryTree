import pytest
import random
from pytree import KDTree, KDT_Node


def is_binary(kdtree) -> bool:

    def traversal_check(node: KDT_Node, depth: int = 0) -> bool:
        # keep going down the chain of nodes
        # until the leftmost/rightmost node has been reached
        # then, return True, as leaf nodes has no child nodes
        if node is None:
            return True

        cd = depth % node.dimension

        left_check = traversal_check(node.left, cd + 1)
        right_check = traversal_check(node.right, cd + 1)

        # check whether the left & right node obey the BST invariant
        check_binary = left_check and right_check

        # then, check the node itself, whether it obeys the BST invariant
        if node.left and node.left.value[cd] > node.value[cd]:
            check_binary = False
        if node.right and node.right.value[cd] < node.value[cd]:
            check_binary = False

        return check_binary

    return traversal_check(kdtree.root)


@pytest.fixture
def kdtree():
    return KDTree()


@pytest.fixture
def filled_kdtree(kdtree: KDTree):
    kdtree.extend([(0, 1), (10, 5), (8, 4), (2, 4), (8, 8)])
    return kdtree


def test_insertion(kdtree: KDTree):
    for _ in range(10):
        kdtree.insert((random.randint(0, 100), random.randint(0, 100)))
    assert is_binary(kdtree)


@pytest.mark.parametrize(
    't_point, expected',
    [((0, 1), (0, 1)), ((69, 69), None), ((-69, -69), None)],
    ids=['valid', '+ invalid', '- invalid']
)
def test_find(filled_kdtree: KDTree, t_point, expected):
    assert filled_kdtree.find(t_point) == expected


@pytest.mark.parametrize(
    't_point, expected',
    [((0, 1), None), ((69, 69), (10, 5)), ((2, 4), (0, 1))],
    ids=['< min', '> max', 'valid']
)
def test_find_lt_node(filled_kdtree: KDTree, t_point, expected):
    assert filled_kdtree.find_lt(t_point) == expected


@pytest.mark.parametrize(
    't_point, expected',
    [((-100, -100), (0, 1)), ((69, 69), None), ((0, 1), (2, 4))],
    ids=['< min', '> max', 'valid']
)
def test_find_gt_node(filled_kdtree: KDTree, t_point, expected):
    assert filled_kdtree.find_gt(t_point) == expected


@pytest.mark.parametrize(
    't_point, expected',
    [((0, -1), (0, 1)), ((69, 69), (10, 5)), ((2, 4), (0, 1))],
    ids=['< min', '> max', 'valid']
)
def test_find_le_node(filled_kdtree: KDTree, t_point, expected):
    assert filled_kdtree.find_le(t_point) == expected


@pytest.mark.parametrize(
    't_point, expected',
    [((-100, -100), (0, 1)), ((69, 69), None), ((0, 1), (0, 1))],
    ids=['< min', '> max', 'valid']
)
def test_find_ge_node(filled_kdtree: KDTree, t_point, expected):
    assert filled_kdtree.find_ge(t_point) == expected


@pytest.mark.parametrize(
    't_point, expected',
    [((-100, -100), (0, 1)), ((69, 69), (8, 8)), ((1, 1), (0, 1))],
    ids=['< min', '> max', 'valid']
)
def test_nearest_neighbour_search(filled_kdtree: KDTree, t_point, expected):
    assert filled_kdtree.query(t_point)[0][0] == expected


@pytest.mark.parametrize(
    'area, expected',
    [
        ((0, 0, 100, 100), [(0, 1), (10, 5), (8, 4), (2, 4), (8, 8)]),
        ((0, 0, 7, 7), [(0, 1), (2, 4)])
    ],
    ids=['max bbox', 'valid']
)
def test_bbox_search(filled_kdtree: KDTree, area, expected):
    filled_kdtree.range(*area) == expected


def test_bbox_resize_after_insertion(kdtree: KDTree):
    points = [(0, 10), (10, 1), (10, 10), (0, 1)]
    for point in points:
        kdtree.insert(point)

    x, y, w, h = kdtree.bbox
    assert (x, y, w, h) == (0, 1, 10, 9)


def test_bbox_resize_after_deletion(filled_kdtree: KDTree):
    for point in filled_kdtree:
        filled_kdtree.delete(point)
        assert point not in filled_kdtree

    x, y, w, h = filled_kdtree.bbox
    assert (x, y, w, h) == (0, 0, 0, 0)
