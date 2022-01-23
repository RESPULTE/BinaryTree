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
    rand_index = -random.randint(1, len(num_gen))
    assert filled_bst[rand_index] == \
        filled_bst.traverse()[rand_index]


def test_find_max(filled_bstree):
    assert filled_bstree.find_max() == 14


def test_find_min(filled_bstree):
    assert filled_bstree.find_min() == 6


@pytest.mark.parametrize('t_val, ex_val', [(8, 9), (100, None), (0, 6)],
                         ids=['normal', '> max', '< min'])
def test_find_gt(filled_bstree, t_val, ex_val):
    assert filled_bstree.find_gt(t_val) == ex_val


@pytest.mark.parametrize('t_val, ex_val', [(8, 6), (5, None), (10, 9)],
                         ids=['normal', '< min', '> max'])
def test_find_lt(filled_bstree, t_val, ex_val):
    assert filled_bstree.find_lt(t_val) == ex_val


def test_find_ge(filled_bstree):
    assert filled_bstree.find_max() == 14


def test_find_le(filled_bstree):
    assert filled_bstree.find_min() == 6


def test_find_value_with_invalid_dtype(filled_bstree: BSTree):
    with pytest.raises(TypeError):
        filled_bstree.find(None)
    with pytest.raises(TypeError):
        filled_bstree.find_ge(None)
    with pytest.raises(TypeError):
        filled_bstree.find_lt(None)
    with pytest.raises(TypeError):
        filled_bstree.find_gt(None)
    with pytest.raises(TypeError):
        filled_bstree.find_le(None)


def test_uncomparable_dtype_insertion(bstree: BSTree):
    uncomparables = [100, 204, 293.203, 'kjdbfvk', True, None]
    with pytest.raises(TypeError):
        for data in uncomparables:
            bstree.insert(data)


def test_invalid_dtype_deletion(filled_bstree: BSTree):
    invalid_data = None
    with pytest.raises(TypeError):
        filled_bstree.delete(invalid_data)


def test_invalid_value_deletion(tree: BSTree):
    tree.insert(100)
    invalid_data = 1
    with pytest.raises(ValueError):
        tree.delete(invalid_data)


def test_find_valid_value(filled_bstree: BSTree):
    rand_val = random.choice(filled_bstree.traverse())
    found_val = filled_bstree.find(rand_val)
    assert found_val == rand_val


def test_pop_from_empty_tree(tree: BSTree):
    with pytest.raises(IndexError):
        tree.pop()


def test_find_from_empty_tree(tree: BSTree):
    assert tree.find(10) is None
    assert tree.find_ge(10) is None
    assert tree.find_lt(10) is None
    assert tree.find_gt(10) is None
    assert tree.find_le(10) is None
    assert tree.find_max() is None
    assert tree.find_min() is None


@pytest.mark.parametrize('order', ['lvl', 'in', 'pre', 'post'])
def test_valid_traversal_key(filled_bstree: BSTree, order: str):
    assert set([6, 8, 10, 9, 12, 11, 14]) == set(filled_bstree.traverse(order))


@pytest.mark.parametrize('order', ['level', 'inlol'])
def test_invalid_traversal_key(filled_bstree: BSTree, order: str):
    with pytest.raises(ValueError):
        filled_bstree.traverse(key=order)
