from typing import List, Tuple
import pytest

from pytree import AVLTree


def is_strict_balanced(tree) -> bool:
    '''
    check whether the tree is balanced, i.e both side of the tree,
    left & right have similar/same number of nodes
    -> the difference in number of nodes for both side
        of every node does not exceed 1

    STEPS:

        1. go down until the leftmost & rightmost node has been reached
        2. start checking whether each node is balanced
        3. return their height along with whether they're balanced or not
        4. unfold the recursion to the prev node
        5. rinse & repeat until the recursion unfolds
            back to the starting node/root node

        * so, if any one of the node, starting from the leaf nodes,
        is unbalanced it will cause will the other nodes 'above'
        him to be unbalanced as well due to all to them depending on
        the last node's balance_value(boolean)

        * basically, only 2 value is passed around,
            the balance_value & the height of the node
            - the balance_value is required for the said chain reaction
            - while the node's height is required for the checking
    '''

    def traversal_check(node) -> Tuple[bool, int]:
        # keep going down the chain of nodes
        # until the leftmost/rightmost node has been reached
        # return True, as leaf nodes has no child nodes and are balanced
        # + the height of the leaf node, which is -1 since it has no child
        if node is None:
            return (True, -1)

        left_height = traversal_check(node.left)
        right_height = traversal_check(node.right)

        # check whether the left & right node is balanced
        # and whether the height the node is balanced
        balanced = (left_height[0] and right_height[0]
                    and abs(left_height[1] - right_height[1]) <= 1)  # noqa

        # return the 'balanced' variable and the height of the current node
        return (balanced, 1 + max(left_height[1], right_height[1]))

    return traversal_check(tree.root)[0]


@pytest.fixture
def avltree():
    return AVLTree()


@pytest.fixture
def filled_avltree(avltree: AVLTree):
    avl_node = avltree._node_type
    avl_root = avltree.root

    avl_root.value = 10
    avl_root.height = 2

    avl_root.left = avl_node(value=8, parent=avl_root, height=1)
    avl_root.right = avl_node(value=12, parent=avl_root, height=1)

    avl_root.left.left = avl_node(value=6, parent=avl_root.left)
    avl_root.left.right = avl_node(value=9, parent=avl_root.left)

    avl_root.right.right = avl_node(value=14, parent=avl_root.right)
    avl_root.right.left = avl_node(value=11, parent=avl_root.right)

    return avltree


def test_strict_balance_in_insertion(binarytester, num_gen: List[int], avltree: AVLTree):
    for val in num_gen:
        avltree.insert(val)
        assert is_strict_balanced(avltree)
        assert binarytester(avltree)


def test_strict_balance_in_deletion(binarytester, filled_avltree: AVLTree):
    for val in filled_avltree:
        filled_avltree.delete(val)
        assert is_strict_balanced(filled_avltree)
        assert val not in filled_avltree
        assert binarytester(filled_avltree)

    assert filled_avltree.traverse() == [] and filled_avltree.root.value is None
