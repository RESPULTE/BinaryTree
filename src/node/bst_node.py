from dataclasses import dataclass, field
from .type_hint import *

@dataclass
class BST_Node(Generic[CT]):


    value:  Optional[CT]     = None
    parent: Optional['BST']  = field(default=None, repr=False, compare=False)
    left:   Optional['BST']  = field(default=None, repr=False, compare=False)
    right:  Optional['BST']  = field(default=None, repr=False, compare=False)

    @property
    def grandparent(self):
        try:
            return self.parent.parent
        except AttributeError:
            return False

    @property
    def uncle(self):
        try:
            return self.grandparent.right if self.parent is self.grandparent.left else self.grandparent.left
        except AttributeError:
            return False

    @property
    def sibling(self):
        try:
            return self.parent.left if self is self.parent.right else self.parent.right
        except AttributeError:
            return False


    def insert(self, value: CT) -> None:
        '''insert a value into the binary tree'''
        if self.value is None:  
            self.value = value
            return 
        self._insert(value)


    def _insert(self, value: CT) -> None:
        '''internal function of the binary tree where the recursions happen'''
        if value == self.value: 
            return None

        if value < self.value:
            if self.left is None:
                self.left = self.__class__(value, parent=self)
                return self.left 
            else:
                return self.left._insert(value)

        elif value > self.value:
            if self.right is None:
                self.right = self.__class__(value, parent=self)
                return self.right
            else:
                return self.right._insert(value)


    def find(self, value: CT) -> CT:
        '''search for the given value in the binary tree'''
        if self.value == value: 
            return self
        if value < self.value and self.left != None:
            return self.left.find(value)
        elif value > self.value and self.right != None:
            return self.right.find(value)
        return None


    def find_min(self):
        '''find the minimum value relative to a specific node in the binary tree'''
        if self.left is None:
            return self
        return self.left.find_min()     


    def find_max(self):
        '''find the maximum value relative to a specific node in the binary tree'''
        if self.right is None:
            return self
        return self.right.find_max() 


    def find_min_by_node(self):
        '''find the minimum value relative to a specific node in the binary tree'''
        if self.left is None:
            return self
        return self.left.find_min_by_node()     


    def find_max_by_node(self):
        '''find the maximum value relative to a specific node in the binary tree'''
        if self.right is None:
            return self
        return self.right.find_max_by_node()    


    def delete(self, value: CT) -> None:
        '''remove the given vaue from the binary tree'''

        node_to_delete = self.find(value)
        
        if node_to_delete is None:
            raise ValueError(f'{value} is not in {self.__class__.__name__}')

        node_to_delete._delete_node()   


    def _delete_node(self): 
        '''
        recursively going down the chain of nodes until a node with only 1 child or no chi.ld is found
        then, perform necceesarily steps to make the node obselete (set to None)
         '''

        # CASE 1: if the node does not have any child
        #  
        #  if the node is not the root node, check the role of the node(right child/left child)
        #  --> then, destroy the node's relationship with its parent
        #  if the node is the root node, set its value to None
        if self.left is None and self.right is None:
            if self.parent != None:
                if self.parent.left == self:
                    self.parent.left = None
                else:
                    self.parent.right = None
            else:
                self.value = None

        # CASE 2: if the node has a left child and a right child
        # 
        #  --> get the child with the minimum value relative to the right child / 
        #      get the child with the maximum value relative to the left child 
        #      and recursively going down the chain from that child's position until a succesful deletion
        #
        #  this will ensure that the chosen child fits the parent's position (doesn't violate any BST invariants), because
        #    - if the child is the one with the maximum value relative to the left child
        #      - replacing the parent with its value guarentees that all the child that's on the left 
        #        has 'smaller' value than 'him' and all the child on the right has bigger value than him
        #        [otherwise there's something wrong with the insertion to begin with]
        #
        #    * Vice versa for the other case (if the child is the one with the minimum value relative to the right child)
        #
        # NOTE TO SELF:
        # consider the following example:
        # - the node to be deleted is the root node [7]
        #
        #   - the successor node in this case would be [8], 
        #     since it is the one with the minimum value relative to the right child of the root node
        #
        #     - [8] will be 'promoted' as the new root node / swap its value with the node to be deleted
        #
        #       (This essentially 'deletes' the node since it has its original value replaced, 
        #        even though that the underlying object of the node is still the same 
        #        {i.e no new node has been created in the process})
        #       
        #       - the < _delete_node > function will then be called upon the original [8] node, 
        #         in which the CASE 3 will be activated since there only ever will be at most 1 child for [8]
        #         or else [8] wouldn't have been the minimum node 
        #            7
        #         /      \
        #        3        9
        #      /   \     /  \
        #     1     5   8    10 
        #    / \   / \   \
        #   0   2 4   6   8.5
        #              
        #                 
        #            8
        #         /      \
        #        3        9
        #      /   \     /  \
        #     1     5   8.5  10 
        #    / \   / \  
        #   0   2 4   6 
        elif self.left and self.right:
            successor_node = self.right.find_min_by_node()
            self.value = successor_node.value 
            successor_node._delete_node()

        # CASE 3: if the node only have one child
        # 
        #  --> check the child's relationship with the node
        #
        #      if the node has a parent (i.e not the root node),
        #  ----> then, create a parent-child relationship between the node's parent and the child
        #        with respect to the child's relationship with the node (right child/left child)
        #
        #      if the node does not have a parent (i.e is a root node)
        #  ----> then, set the child's value as it's own and 
        #        recursively go down the chain from the child's position until a succesful deletion
        else:
            child_node = self.left if self.left != None else self.right

            if self.parent != None:
                child_node.parent = self.parent

                if self.parent.left == self:
                    self.parent.left = child_node

                else:
                    self.parent.right = child_node

            else:
                self.__dict__ = child_node.__dict__

                if child_node.right != None:
                    child_node.right.parent = self
                if child_node.left != None:
                    child_node.left.parent = self
                    
                self.parent = None

    def __str__(self):
        return str(self.value)


    def __repr__(self):
        family_val = ( member.value if member != None else None for member in [self, self.parent, self.left, self.right])
        return f'self: {next(family_val)} | parent: {next(family_val)} | left: {next(family_val)} | right: {next(family_val)}'
