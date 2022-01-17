from typing import Any

from pytree.binarytree._tree import BinaryTree
from .type_hints import Num, Point
from .kdt_node import KDT_Node


class KDTree(BinaryTree):

    _node_type = KDT_Node

    def __init__(self, dimension: int = 2):
        super().__init__()
        self.root.dimension = dimension

    @property
    def is_binary(self) -> bool:

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
                print(node, node.left, node.right, cd)
            if node.right and node.right.value[cd] < node.value[cd]:
                check_binary = False
                print(node, node.left, node.right, cd)

            return check_binary

        return traversal_check(self.root)

    def find_closest(self,
                     target_point: Point,
                     *,
                     num: int = 1,
                     radius: Num = 0,
                     dist: bool = False) -> KDT_Node:
        closest_nodes = self.root.find_closest_node(target_point, num)
        if dist or radius:
            point_and_dist = [(node.value, round(sqdist**0.5, 3))
                              for sqdist, node in closest_nodes]
            if not radius:
                return point_and_dist
            return list(filter(lambda pnd: pnd[1] <= radius, point_and_dist))
        return [node.value for _, node in closest_nodes]
