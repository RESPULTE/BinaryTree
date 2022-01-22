from typing import List
import pytest
import random

from pytree import BinaryTree, BSTree, AVLTree, RBTree, SplayTree


def is_binary(tree) -> bool:
    '''
    check whether the tree obeys the binary search tree's invariant
    i.e:
    - left node's value < node's value
    - right node's value > node's value
    '''

    def traversal_check(node) -> bool:
        # keep going down the chain of nodes
        # until the leftmost/rightmost node has been reached
        # then, return True, as leaf nodes has no child nodes
        if node is None:
            return True

        left_check = traversal_check(node.left)
        right_check = traversal_check(node.right)

        # check whether the left & right node obey the BST invariant
        check_binary = left_check and right_check

        # then, check the node itself, whether it obeys the BST invariant
        if node.left and node.left >= node:
            check_binary = False
        if node.right and node.right < node:
            check_binary = False

        return check_binary

    return traversal_check(tree.root)


@pytest.fixture
def binarytester():
    return is_binary


@pytest.fixture
def num_gen() -> List[int]:
    return list(set([random.randint(0, 1000) for _ in range(100)]))


@pytest.fixture(params=[BSTree, AVLTree, RBTree, SplayTree])
def tree(request: BinaryTree) -> BinaryTree:
    return request.param()


@pytest.fixture(params=[BSTree, AVLTree, RBTree, SplayTree])
def filled_tree(num_gen: List[int], request: BinaryTree) -> BinaryTree:
    return request.param.fill_tree(num_gen)
