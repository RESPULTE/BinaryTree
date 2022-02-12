from dataclasses import dataclass
from typing import Union

from pytree.Binarytree._type_hint import CT
from pytree.Binarytree.Node.bst_node import BST_Node


@dataclass(order=True, slots=True)
class Splay_Node(BST_Node):
    '''
    - the node class for the splay tree
    - self-adjusting, recently searched/inserted/deleted node will be moved
      to the top for faster access
    - for internal use only, shouldn't be used independently
    '''

    def _update_node(self) -> None:
        '''
        internal function for the splay tree's node
        recursively move the intended node up until it is the root node
        '''
        if self.parent is None:
            return self

        if self is self.parent.right:
            self.parent._rotate_left()

        elif self is self.parent.left:
            self.parent._rotate_right()

        return self._update_node()

    def insert_node(self, value: CT) -> None:
        '''
        add a node with the given value into the tree
        update/splay the node to the root upon a succesfully insert
        returns a node to be designated as the 'root node'
        if the value is succesfully inserted
        '''
        new_node = self._insert_node(value)

        if new_node:
            new_node._update_node()

    def delete_node(self, node_to_delete: 'Splay_Node') -> None:
        '''
        remove the node that contains the given value from the tree
        update/splay the parent of the
        deleted node to the root upon a succesfully delete
        returns a node to be designated as the 'root node'
        if the value is succesfully deleted
        '''
        node_to_splay = node_to_delete.parent

        node_to_delete._delete_node()

        if node_to_splay is not None:
            node_to_splay._update_node()
