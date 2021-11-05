from dataclasses import dataclass, field

from .bbst_node import BBST_Node
from .type_hint import *


@dataclass
class AVL_Node(BBST_Node):


    height: int   = field(default=0, compare=False)
    b_factor: int = field(default=0, compare=False)


    def _update(self) -> None:
        self._update_determinant()      

        if self.b_factor > 1 or self.b_factor < -1: 
            self._rebalance()  

        if self.parent != None: 
            return self.parent._update()

        return self


    def insert(self, value: CT) -> Union['BBST', None]:
        new_node = self._insert(value)
        if new_node: 
            # only update the node if a new node has been inserted into the binary tree
            # the '_insert' function will return None if the value already exists in the binary tree
            return new_node._update() 


    def delete(self, value: CT) -> None: 
        new_root = None 

        node_to_delete = self.find(value) 

        node_to_delete._delete_node()

        new_root = node_to_delete._update()

        return new_root


    def _rebalance(self) -> None:
        '''performs neccessary rotations based on the balancing factor of the node'''
        if self.b_factor == -2:
            if self.left.b_factor <= 0:
                # left-left case
                # a straight line in formed with 
                # the node, node's left_child & node's left_grandchild
                #
                #        X(node)
                #       /
                #      Y (node's grandchild)
                #     /
                #    Z (node's child)
                #
                self._rotate_right()
            else:
                # left-right case
                # a corner/v-shape to the left in formed with 
                # the node, node's left_child & node's left_grandchild
                #
                #    X(node)
                #   /
                #  Y (node's child)
                #   \
                #    Z (node's grandchild)
                #
                # gotta rotate the node's left_child first so that
                # a line between those 3 nodes can be formed
                # since the node's grandchild is'larger' than node's child
                # the rotation will not affect the invariants of a Binary Search Tree
                # i.e the rules of BST
                #
                #        X(node)
                #       /
                #      Y (node's grandchild)
                #     /
                #    Z (node's child)
                #
                # P.S: The node's parent is ommitted here to avoid over-complicating everything
                self.left._rotate_left()
                self._rotate_right()

        if self.b_factor == +2:
            if self.right.b_factor >= 0:
                # right-right case
                # a straight line in formed with 
                # the node, node's right_child & node's right_grandchild
                #
                #  X(node)
                #   \
                #    Y (node's grandchild)
                #     \
                #      Z (node's child)
                #
                self._rotate_left()
            else:
                # right-left case
                # a corner/v-shape to the right in formed with 
                # the node, node's left_child & node's left_grandchild
                #    X(node)
                #     \
                #      Y (node's child)
                #     /
                #    Z (node's grandchild)
                #
                # gotta rotate the node's left_child first so that
                # a line between those 3 nodes can be formed
                # since the node's grandchild is 'smaller' than node's child
                # the rotation will not affect the invariants of a Binary Search Tree
                # i.e the rules of BST
                #
                #  X(node)
                #   \
                #    Y (node's grandchild)
                #     \
                #      Z (node's child)
                #
                # P.S: The node's parent is ommitted here to avoid over-complicating everything
                self.right._rotate_right()
                self._rotate_left()

        if self.grandparent != None:
            self.grandparent._update_determinant()
        self.parent._update_determinant()
        self._update_determinant()


    def _update_determinant(self) -> None:
        '''
        update the height and balancing factor for the specific node
        -> to be used for the rebalance method
        '''
        # setting -1 as the default value if a node doesnt exist
        # since the height of a leaf node is by default 0
        left_height   = self.left.height if self.left else -1 
        right_height  = self.right.height if self.right else -1 

        # getting the highest tree out of the 2 (left_child & right_child of the node)
        # and adding 1 to it for the new height of the node
        self.height   = 1 + max(left_height, right_height)

        # get the balancing factor of the node 
        # based on how 'balanced' its left_child and right_child is
        # i.e how similar they are in terms of their height
        self.b_factor = right_height - left_height





