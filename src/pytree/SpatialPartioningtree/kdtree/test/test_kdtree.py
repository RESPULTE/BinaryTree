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
def filled_kdtree():
    return KDTree.fill_tree([(0, 1), (10, 5), (8, 4), (2, 4), (8, 8)])


def test_insertion(kdtree: KDTree):
    for _ in range(10):
        kdtree.insert((random.randint(0, 100), random.randint(0, 100)))
    assert is_binary(kdtree)


def test_find_node(filled_kdtree: KDTree):
    pass


def test_find_lt_node(filled_kdtree: KDTree):
    ...


def test_find_gt_node(filled_kdtree: KDTree):
    ...


def test_find_le_node(filled_kdtree: KDTree):
    ...


def test_find_ge_node(filled_kdtree: KDTree):
    ...


def test_nearest_neighbour_search(filled_kdtree: KDTree):
    ...


def test_bbox_search(filled_kdtree: KDTree):
    ...


def test_radial_search(filled_kdtree: KDTree):
    ...


def test_deletion(filled_kdtree: KDTree):
    pass
