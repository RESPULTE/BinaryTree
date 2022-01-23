from typing import List
import pytest

from pytree import BinaryTree, AVLTree, BSTree, RBTree, SplayTree


@pytest.mark.parametrize('data_gen, tree', [
    ('num_gen', BSTree),
    ('num_gen', AVLTree),
    ('num_gen', SplayTree),
    ('num_gen', RBTree)
])
def test_tree_addition(data_gen: List[int], tree: BinaryTree):
    orig_tree = tree.fill_tree(data_gen)
    tree_1 = tree.fill_tree(data_gen[0: 49])
    tree_2 = tree.fill_tree(data_gen[50: 99])

    sum_tree = tree_1 + tree_2
    assert sum_tree.traverse() == orig_tree.traverse()


@pytest.mark.parametrize('data_gen, tree', [
    ('num_gen', BSTree),
    ('num_gen', AVLTree),
    ('num_gen', SplayTree),
    ('num_gen', RBTree)
])
def test_tree_total_subtraction(data_gen: List[int], tree: BinaryTree):
    tree_1 = tree.fill_tree(data_gen)
    tree_2 = tree.fill_tree(data_gen)
    diff_tree = tree_1 - tree_2

    assert diff_tree.traverse() == []


def test_tree_subtraction(tree_obj: BinaryTree):
    tree_1 = tree_obj.fill_tree([i for i in range(100)])
    tree_2 = tree_obj.fill_tree([i for i in range(50)])
    diff_tree = tree_1 - tree_2

    assert diff_tree.traverse() == [i for i in range(50, 100)]


def test_tree_difference(tree_obj: BinaryTree):
    tree_1 = tree_obj.fill_tree([i for i in range(100)])
    tree_2 = tree_obj.fill_tree([i for i in range(50)])
    assert tree_1.difference(tree_2).traverse() == [i for i in range(50, 100)]


def test_tree_superset(tree_obj: BinaryTree):
    tree_1 = tree_obj.fill_tree([i for i in range(100)])
    tree_2 = tree_obj.fill_tree([i for i in range(50)])
    assert tree_1.is_superset(tree_2)


def test_tree_subset(tree_obj: BinaryTree):
    tree_1 = tree_obj.fill_tree([i for i in range(100)])
    tree_2 = tree_obj.fill_tree([i for i in range(50)])
    assert tree_2.is_subset(tree_1)


def test_tree_disjoint(tree_obj: BinaryTree):
    tree_1 = tree_obj.fill_tree([i for i in range(50, 100)])
    tree_2 = tree_obj.fill_tree([i for i in range(50)])
    assert tree_2.is_disjoint(tree_1)


def test_tree_intersection(tree_obj: BinaryTree):
    tree_1 = tree_obj.fill_tree([i for i in range(100)])
    tree_2 = tree_obj.fill_tree([i for i in range(50)])
    assert tree_2.intersection(tree_1).traverse() == [i for i in range(50)]
