from dataclasses import dataclass, field
from pytree.binarytree._type_hint import *
from .bst_node import BST_Node


@dataclass
class AVL_Node(BST_Node):
    '''
    The node class for the AVL tree

    ALL INVARIANTS:

        i. the height of every node must not exceed 1 / -1
            - exceeding (1) -> right-skewed
            - exceeding (-1)-> left-skewed

        ii. node without any child node will be considered to have a height of -1


    P.S the value for the invariants can be changed depending on how its implemented

    '''

    height: int   = field(default=0, compare=False)
    b_factor: int = field(default=0, compare=False)


    def insert_node(self, value: CT) -> Union['AVL_Node', None]:
        new_node = self._insert_node(value)
        if new_node: 
            # only update the node if a new node has been inserted into the binary tree
            # the '_insert_node' function will return None if the value already exists in the binary tree
            return new_node._update_node() 


    def delete_node(self, node_to_delete: 'AVL_Node') -> Union['AVL_Node', None]: 
        deleted_node = node_to_delete._delete_node()

        # using the parent of the node that has been 'deleted' to do the update
        # because the node isn't actually deleted, it either 
        # - had its relationship with its parent cut off -> can't be accessed
        # - had its value overwritten by a child node
        new_root = deleted_node._update_node()

        return new_root


    def _update_node(self) -> 'AVL_Node':
        '''
        internal function of the AVL node

        responsible for:
        - updating the balancing factor and height of nodes
        - doing the neccessary rotations that is invloved
        '''
        self._update_node_status()      

        if self.b_factor > 1 or self.b_factor < -1: 
            self._rebalance()  

        # keep going until the root node is reached
        # then, just return the node for caching in the <Tree> class
        if self.parent != None: 
            return self.parent._update_node()

        return self


    def _rebalance(self) -> None:
        '''
        performs neccessary rotations based on the balancing factor of the node
        updates the balancing factor of the node and the height
        -> to be used for the '_update_node' method
        '''
        # ROTATION PHASE
        # the node is skewed to the left / 'left heavy'
        if self.b_factor == -2:
            if self.left.b_factor <= 0:
                self._rotate_right()
            else:
                self.left._rotate_left()
                self._rotate_right()

        # the node is skewed to the right / 'right heavy'
        if self.b_factor == +2:
            if self.right.b_factor >= 0:
                self._rotate_left()
            else:
                self.right._rotate_right()
                self._rotate_left()

        # UPDATING PHASE
        if self.grandparent != None:
            self.grandparent._update_node_status()
        self.parent._update_node_status()
        self.parent.right._update_node_status()
        self.parent.left._update_node_status()


    def _update_node_status(self) -> None:
        '''
        update the height and balancing factor for the specific node
        -> to be used for the '_rebalance' method
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