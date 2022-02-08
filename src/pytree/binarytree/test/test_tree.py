from typing import List
import pytest

from pytree import BinaryTree, AVLTree, BSTree, RBTree, SplayTree


def test_addition(num_gen: List[int], tree_obj: BinaryTree):
    orig_tree = tree_obj.fill_tree(num_gen)
    tree_1 = tree_obj.fill_tree(num_gen[0: 50])
    tree_2 = tree_obj.fill_tree(num_gen[50: 100])

    sum_tree = tree_1 + tree_2
    assert sum_tree.traverse() == orig_tree.traverse()


def test_total_subtraction(num_gen: List[int], tree_obj: BinaryTree):
    tree_1 = tree_obj.fill_tree(num_gen)
    tree_2 = tree_obj.fill_tree(num_gen)
    diff_tree = tree_1 - tree_2

    assert diff_tree.traverse() == []


def test_subtraction(tree_obj: BinaryTree, num_gen):
    tree_1 = tree_obj.fill_tree(num_gen)
    tree_2 = tree_obj.fill_tree(num_gen[0: 50])
    diff_tree = tree_1 - tree_2

    assert set(diff_tree.traverse()) == set(num_gen[50: 100])


def test_difference(tree_obj: BinaryTree, num_gen):
    tree_1 = tree_obj.fill_tree(num_gen)
    tree_2 = tree_obj.fill_tree(num_gen[0: 50])
    assert set(tree_1.difference(tree_2).traverse()) == set(num_gen[50: 100])


def test_superset(tree_obj: BinaryTree, num_gen):
    tree_1 = tree_obj.fill_tree(num_gen)
    tree_2 = tree_obj.fill_tree(num_gen[0: 50])
    assert tree_1.is_superset(tree_2)


def test_subset(tree_obj: BinaryTree, num_gen):
    tree_1 = tree_obj.fill_tree(num_gen)
    tree_2 = tree_obj.fill_tree(num_gen[0: 50])
    assert tree_2.is_subset(tree_1)


def test_disjoint(tree_obj: BinaryTree, num_gen):
    tree_1 = tree_obj.fill_tree(num_gen[50: 100])
    tree_2 = tree_obj.fill_tree(num_gen[0: 50])
    assert tree_2.is_disjoint(tree_1)


def test_intersection(tree_obj: BinaryTree, num_gen):
    tree_1 = tree_obj.fill_tree(num_gen)
    tree_2 = tree_obj.fill_tree(num_gen[0: 50])
    assert set(tree_2.intersection(tree_1).traverse()) == set(num_gen[0: 50])


def test_pickle(num_gen, tmpdir):
    orig_tree = BSTree.fill_tree(num_gen)
    data_file = str(tmpdir.join('test_pickle'))
    orig_tree.pickle(data_file)
    new_tree = BSTree.load_pickle(data_file)
    assert set(new_tree.traverse()) == set(orig_tree.traverse())
