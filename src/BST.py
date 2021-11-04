from dataclasses import dataclass, field
from typing import Generic, Any, Optional, TypeVar, List, Union, ClassVar
from collections import deque

T = TypeVar('T', bound=Any)


@dataclass
class BST(Generic[T]):


    value:  Optional[T]      = None
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

    @classmethod
    def fill_tree(cls, values: List[T]) -> 'BST':
        '''generates a binary tree with all the values from a list'''
        new_bst = cls()
        for value in values:
            new_bst.insert(value)
        return new_bst


    def insert(self, value: T) -> None:
        '''insert a value into the binary tree'''
        if self.value is None:  
            self.value = value
        self._insert(value)


    def _insert(self, value: T) -> None:
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


    def find(self, value: T) -> T:
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


    def traverse(self, key='in') -> List[T]:
        '''
        returns a list containing all the items in the binary tree in the given order type
        in-order  ['in']: from min-to-max
        pre-order ['pre']: root node as the beginning, from left to right, kinda like DFS
        post-order ['post']: root node as the end, from left to right
        level-order ['lvl']: from top-to-bottom, left-to-right, kinda like BST
        '''
        def inorder_traversal(node: 'BST', path: list):
            if node.left:
                inorder_traversal(node.left, path)
            path.append(node.value)
            if node.right:
                inorder_traversal(node.right, path)
            return path

        def postorder_traversal(node: 'BST', path: list):
            if node.left:
                postorder_traversal(node.left, path)
            if node.right:
                postorder_traversal(node.right, path)
            path.append(node.value)
            return path

        def preorder_traversal(node: 'BST', path: list):
            path.append(node.value)
            if node.left:
                preorder_traversal(node.left, path)
            if node.right:
                preorder_traversal(node.right, path)
            return path

        def levelorder_traversal(node: 'BST', path: list):
            stack = deque([self])

            while stack != deque([]):
                node = stack.popleft()
                path.append(node.value)

                if node.left != None: 
                    stack.append(node.left)
                if node.right != None: 
                    stack.append(node.right)

            return path

        traversing_option = {
        'in': inorder_traversal, 
        'post': postorder_traversal, 
        'pre': preorder_traversal,
        'lvl': levelorder_traversal
        }

        if key not in traversing_option:
            raise ValueError(f'{key} given is not a valid option')

        return traversing_option[key](self, [])


    def delete(self, value: T) -> None:
        '''remove the given vaue from the binary tree'''

        node = self.find(value)
        if node == None:
            raise ValueError(f'{value} is not in {self.__class__.__name__}')

        node._delete_node()   


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
                
            return self

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

            return successor_node._delete_node()

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
                return child_node
            else:
                self.value = child_node.value
                return child_node._delete_node()


    def __add__(self, other: Union['BST', T]) -> 'BST':
        if isinstance(other, type(self)):
            total_val = self.traverse()
            for val in other:
                if val not in self:
                    total_val.append(val)
            return BST.fill_tree(total_val)

        new_bst = BST.fill_tree(self.traverse())
        new_bst.insert(other)
        return new_bst


    def __iadd__(self, other: Union['BST', T]) -> 'BST':
        if isinstance(other, type(self)):
            for val in other:
                if val not in self:
                    self.insert(val)
            return self

        self.insert(other)
        return self


    def __sub__(self, other: Union['BST', T]) -> 'BST':
        if isinstance(other, type(self)):
            total_val = self.traverse()
            for val in other:
                if val in self:
                    total_val.remove(val)
            return BST.fill_tree(total_val)

        new_bst = BST.fill_tree(self.traverse())
        new_bst.delete(other)
        return new_bst


    def __isub__(self, other: Union['BST', T]) -> 'BST':
        if isinstance(other, type(self)):
            for val in other:
                if val in self:
                    self.delete(val)
            return self
            
        self.insert(other)
        return self


    def __iter__(self):
        return iter((self.traverse()))


    def __contains__(self, value: T) -> bool:
        return True if self.find(value) else False


    def __str__(self):
        return str(self.value)







