from typing import List
import pytest
import random

from pytree import BinaryTree, AVLTree, BSTree, RBTree, SplayTree


def test_uncomparable_dtype_insertion(tree: BinaryTree):
    uncomparables = [100, 204, 293.203, 'kjdbfvk', True, None]
    with pytest.raises(TypeError):
        for data in uncomparables:
            tree.insert(data)


def test_invalid_dtype_deletion(filled_tree: BinaryTree):
    invalid_data = None
    with pytest.raises(TypeError):
        filled_tree.delete(invalid_data)


def test_invalid_value_deletion(tree: BinaryTree):
    tree.insert(100)
    invalid_data = 1
    with pytest.raises(ValueError):
        tree.delete(invalid_data)


def test_find_valid_value(filled_tree: BinaryTree):
    rand_val = random.choice(filled_tree.traverse())
    found_node = filled_tree.find(rand_val, node=True)
    assert found_node.value == rand_val


def test_find_value_with_invalid_dtype(filled_tree: BinaryTree):
    with pytest.raises(TypeError):
        filled_tree.find(None)
    with pytest.raises(TypeError):
        filled_tree.find_ge(None)
    with pytest.raises(TypeError):
        filled_tree.find_lt(None)
    with pytest.raises(TypeError):
        filled_tree.find_gt(None)
    with pytest.raises(TypeError):
        filled_tree.find_le(None)


def test_pop_from_empty_tree(tree: BinaryTree):
    with pytest.raises(IndexError):
        tree.pop()


def test_find_from_empty_tree(tree: BinaryTree):
    assert tree.find(10) is None
    assert tree.find_ge(10) is None
    assert tree.find_lt(10) is None
    assert tree.find_gt(10) is None
    assert tree.find_le(10) is None
    assert tree.find_max() is None
    assert tree.find_min() is None


@pytest.mark.parametrize('order', ['lvl', 'in', 'pre', 'post'])
def test_traversal(num_gen: List[int], filled_tree: BinaryTree, order: str):
    assert set(num_gen) == set(filled_tree.traverse(order))
