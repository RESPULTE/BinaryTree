from typing import Tuple, List
import pytest
from pytree import RBTree


def is_redblack(node) -> Tuple[bool, int]:
    # keep going down the chain of nodes
    # until the leftmost/rightmost node has been reached
    # then, return True, as leaf nodes has no child nodes
    # and are inherently colour-balanced
    # and the 'black_height' of the node,
    # which can be anything really,
    # as it doesnt affect the overall result
    if node is None:
        return (True, 0)

    left_check = is_redblack(node.left)
    right_check = is_redblack(node.right)

    # check whether the left & right node is colour-balanced
    # i.e the number of black nodes in the left subtree
    #     is the same as the right sub-tree
    colour_check = left_check[0] and right_check[0]
    # check whether the nodes obey the red-black invariants
    # i.e a red child cannot have a red parent
    if node.parent and node.parent.is_red and node.is_red:
        colour_check = False

    # get the max height among left and right black heights
    # to get the 'problematic' subtree since both should be the same
    # if things are done properly
    total_black_nodes = max(right_check[1], left_check[1])

    # print(node.value, left_check, right_check)
    # add 1 if the current node that;s being looked at is black
    if not node.is_red:
        total_black_nodes += 1
    return (colour_check, total_black_nodes)


@pytest.fixture
def rbtree():
    return RBTree()


@pytest.fixture
def filled_rbtree(rbtree, num_gen):
    rb_node = rbtree._node_type
    rb_root = rbtree.root

    rb_root.value = 10
    rb_root.is_red = False

    rb_root.left = rb_node(value=8, parent=rb_root, is_red=False)
    rb_root.right = rb_node(value=12, parent=rb_root, is_red=False)

    rb_root.left.left = rb_node(value=6, parent=rb_root.left)
    rb_root.left.right = rb_node(value=9, parent=rb_root.left)

    rb_root.right.right = rb_node(value=14, parent=rb_root.right)
    rb_root.right.left = rb_node(value=11, parent=rb_root.right)

    return rbtree


def test_redblack_invariant_for_insertion(num_gen: List[int], rbtree: RBTree):
    for val in num_gen:
        rbtree.insert(val)
        assert is_redblack(rbtree.root)


def test_redblack_invariant_for_deletion(binarytester, filled_rbtree: RBTree):
    for val in filled_rbtree:
        filled_rbtree.delete(val)
        assert is_redblack(filled_rbtree.root)
        assert binarytester(filled_rbtree)

    assert filled_rbtree.traverse() == [] and filled_rbtree.root.value is None
