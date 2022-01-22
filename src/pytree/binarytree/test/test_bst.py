import random
import pytest
from pytree import BSTree


@pytest.fixture
def bstree():
    return BSTree()


@pytest.fixture
def filled_bstree(bstree: BSTree):
    bs_node = bstree._node_type
    bs_root = bstree.root

    bs_root.value = 10

    bs_root.left = bs_node(value=8, parent=bs_root)
    bs_root.right = bs_node(value=12, parent=bs_root)

    bs_root.left.left = bs_node(value=6, parent=bs_root.left)
    bs_root.left.right = bs_node(value=9, parent=bs_root.left)

    bs_root.right.right = bs_node(value=14, parent=bs_root.right)
    bs_root.right.left = bs_node(value=11, parent=bs_root.right)

    bstree._size = 7
    return bstree


def test_indexing(num_gen):
    filled_bst = BSTree.fill_tree(num_gen)
    rand_index = random.randint(0, len(num_gen) - 1)
    assert filled_bst[rand_index] == \
        filled_bst.traverse()[rand_index]


def test_negative_indexing(num_gen):
    filled_bst = BSTree.fill_tree(num_gen)
    rand_index = - random.randint(1, len(num_gen))
    assert filled_bst[rand_index] == \
        filled_bst.traverse()[rand_index]


def test_find_max(filled_bstree):
    assert filled_bstree.find_max() == 14


def test_find_min(filled_bstree):
    assert filled_bstree.find_min() == 6


@pytest.mark.parametrize('t_val, ex_val', [(8, 9), (100, None), (0, 6)], ids=['normal', '> max', '< min'])
def test_find_gt(filled_bstree, t_val, ex_val):
    assert filled_bstree.find_gt(t_val) == ex_val


@pytest.mark.parametrize('t_val, ex_val', [(8, 6), (5, None), (10, 9)], ids=['normal', '< min', '> max'])
def test_find_lt(filled_bstree, t_val, ex_val):
    assert filled_bstree.find_lt(t_val) == ex_val


def test_find_ge(filled_bstree):
    assert filled_bstree.find_max() == 14


def test_find_le(filled_bstree):
    assert filled_bstree.find_min() == 6
