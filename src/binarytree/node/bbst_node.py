from dataclasses import dataclass
from .bst_node import BST_Node


@dataclass
class BBST_Node(BST_Node):


    def __post_init__(self):
        if self.__class__ == BBST_Node:
            raise TypeError("Cannot instantiate abstract class.")


    def delete(self):
        raise NotImplementedError


    def insert(self):
        raise NotImplementedError
        

    def _update(self):
        raise NotImplementedError


    def get_root(self):
        node = self
        while node.parent != None:
            node = node.parent
        return node


    def is_balanced(self) -> None:
        raise NotImplementedError
        

    def _rotate_left(self) -> None:
        """
        Rotates left:

        Y:  node
        X:  node's right child
        T2: possible node's right child's left child (maybe None)
        P:  possible parent (maybe None) of Y

              p                               P
              |                               |
              x                               y
             / \n     left Rotation          /  \
            y   T3   < - - - - - - -        T1   x 
           / \n                                 / \
          T1  T2                              T2  T3

        the right_child of Y becomes T2
        the left_child of X becomes Y
        the right_child/left_child of P becomes X, depends on X's role
        """
        parent_node = self.parent
        right_node  = self.right
        self.right  = right_node.left

        # set the parent of the T2 to Y if T2 exists
        if right_node.left != None: 
            right_node.left.parent = self

        # set the Y as X's left_child
        right_node.left = self
        # set Y's parent to X
        self.parent = right_node
        # set X's parent to P (Y's original parent)(maybe None)
        right_node.parent = parent_node

        if parent_node != None:
            # set the role of X based of the role of Y (right_child/left_child)
            if parent_node.right == self:
                parent_node.right = right_node
            else:
                parent_node.left = right_node


    def _rotate_right(self) -> None:
        """
        Rotates right:

        Y:  node
        X:  node's left_child
        T2: node's left_child's right_child
        P:  possible parent (maybe None) of Y
              p                           P
              |                           |
              y                           x
             / \n     Right Rotation     /  \
            x   T3   - - - - - - - >    T1   y 
           / \n                             / \
          T1  T2                          T2  T3

        the left_child of Y becomes T2
        the right_child of X becomes Y
        the right_child/left child of P becomes X, depends on X's role
        """
        parent_node = self.parent
        left_node   = self.left
        self.left   = left_node.right

        # set the parent of the T2 to Y if T2 exists
        if left_node.right != None: 
            left_node.right.parent = self

        # set the Y as X's right_child
        left_node.right = self
        # set Y's parent to X
        self.parent = left_node
        # set X's parent to P (Y's original parent) (maybe None)
        left_node.parent = parent_node

        if parent_node != None:
            # set the role of X based of the role of Y (right_child/left_child)
            if parent_node.left == self:
                parent_node.left = left_node
            else:
                parent_node.right = left_node
            

