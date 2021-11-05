from collections import deque
from .node import *


class Tree:

    def __init__(self):
        self.root = None


    @classmethod
    def fill_tree(cls, values) -> 'BST':
        '''generates a binary tree with all the values from a list'''
        new_bst = cls()
        for value in values:
            new_bst.insert(value)
        return new_bst


    def insert(self, value):
        if self.root == None:
            self.root = self._node_type(value)
            return
        new_root = self.root.insert(value)
        if new_root != None:
            self.root = new_root


    def delete(self, value):
        new_root = self.root.delete(value)
        if new_root != None:
            self.root = new_root


    def traverse(self, key='in'):
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
            stack = deque([self.root])

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

        return traversing_option[key](self.root, [])


    def find_node(self, value):
        return self.root.find(value)


    def find_max_node(self):
        return self.root.find_max()


    def find_min_node(self):
        return self.root.find_min()


    def __add__(self, other) -> 'BST':
        if isinstance(other, type(self)):
            total_val = self.traverse()
            for val in other:
                if val not in self:
                    total_val.append(val)
            return self.fill_tree(total_val)

        try:
            return self.fill_tree(self.traverse()).insert(other)
        except:
            raise ValueError(f'cannot insert value of type "{other.__class__.__name__}" into "{self.__class__.__name__}" with value of type "{self.root.value.__class__.__name__}"')


    def __iadd__(self, other) -> 'BST':
        if isinstance(other, type(self)):
            for val in other:
                if val not in self:
                    self.insert(val)
            return self

        try:
            self.insert(other)
            return self
        except:
            raise ValueError(f'cannot insert value of type "{other.__class__.__name__}" into "{self.__class__.__name__} "with value of type "{self.root.value.__class__.__name__}"')


    def __sub__(self, other) -> 'BST':
        if isinstance(other, type(self)):
            total_val = self.traverse()
            for val in other:
                if val in self:
                    total_val.remove(val)
            return self.fill_tree(total_val)

        try:
            return self.fill_tree(self.traverse()).delete(other)
        except:
            raise ValueError(f'cannot delete value of type {type(other)} into {self.__class__.__name__} with value of type "{self.root.value.__class__.__name__}"')



    def __isub__(self, other) -> 'BST':
        if isinstance(other, type(self)):
            for val in other:
                if val in self:
                    self.delete(val)
            return self
        
        try:
            self.insert(other)
            return self
        except:
            raise ValueError(f'cannot delete value of type "{other.__class__.__name__}" into "{self.__class__.__name__}" with value of type "{self.root.value.__class__.__name__}"')


    def __iter__(self):
        return iter((self.traverse()))


    def __contains__(self, value) -> bool:
        return True if self.root.find(value) else False


    def __str__(self):
        return str(self.traverse())










