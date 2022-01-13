from dataclasses import dataclass
from pytree.binarytree._type_hint import CT, N, Union
from .bst_node import BST_Node


@dataclass
class Splay_Node(BST_Node):
    '''
    - the node class for the splay tree
    - self-adjusting, recently searched/inserted/deleted node will be moved
      to the top for faster access
    - for internal use only, shouldn't be used independently
    '''

    def _update_node(self) -> N:
        '''
        internal function for the splay tree's node
        recursively move the intended node up until it is the root node
        '''
        if self.parent is None:
            return self

        if self == self.parent.right:
            self.parent._rotate_left()

        elif self == self.parent.left:
            self.parent._rotate_right()

        return self._update_node()

    def insert_node(self, value: CT) -> Union[None, 'Splay_Node']:
        '''
        add a node with the given value into the tree
        update/splay the node to the root upon a succesfully insert
        returns a node to be designated as the 'root node'
        if the value is succesfully inserted
        '''
        new_node = self._insert_node(value)

        if new_node:
            return new_node._update_node()

    def delete(self,
               node_to_delete: 'Splay_Node') -> Union[None, 'Splay_Node']:
        '''
        remove the node that contains the given value from the tree
        update/splay the parent of the 
        deleted node to the root upon a succesfully delete
        returns a node to be designated as the 'root node'
        if the value is succesfully deleted
        '''
        node_to_splay = node_to_delete.parent

        node_to_delete._delete_node()

        if node_to_splay:
            return node_to_splay._update_node()
