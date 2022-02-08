from textwrap import fill
from typing import List
from numpy import random
import pytest

from pytree import SplayTree


@pytest.fixture
def splaytree():
    return SplayTree()


@pytest.fixture
def filled_splaytree(splaytree):
    splay_node = splaytree._node_type
    splay_root = splaytree.root

    splay_root.value = 10

    splay_root.left = splay_node(value=8, parent=splay_root)
    splay_root.right = splay_node(value=12, parent=splay_root)

    splay_root.left.left = splay_node(value=6, parent=splay_root.left)
    splay_root.left.right = splay_node(value=9, parent=splay_root.left)

    splay_root.right.right = splay_node(value=14, parent=splay_root.right)
    splay_root.right.left = splay_node(value=11, parent=splay_root.right)

    return splaytree


def test_splay_in_insertion(binarytester, num_gen: List[int], splaytree: SplayTree):
    for val in num_gen:
        splaytree.insert(val)
        assert splaytree.root.value == val
        assert binarytester(splaytree)


def test_splay_in_deletion(binarytester, filled_splaytree: SplayTree):
    for val in filled_splaytree:
        node_to_delete = filled_splaytree.find(val)
        filled_splaytree.delete(val)
        if node_to_delete != filled_splaytree.root:
            assert node_to_delete.parent == filled_splaytree.root
        assert binarytester(filled_splaytree)
    assert filled_splaytree.traverse() == [] and filled_splaytree.root.value is None


def test_splay_in_find_methods(filled_splaytree: SplayTree):
    rand_val = filled_splaytree[random.randint(0, 6)]
    filled_splaytree.find(rand_val)
    assert filled_splaytree.root.value == rand_val
