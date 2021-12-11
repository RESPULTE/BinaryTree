from dataclasses import dataclass, field
from ._type_hint import *


@dataclass(order=True)
class BST_Node(Generic[CT]):
    '''
    - a basic binary search tree node
    - has a double reference, i.e the child and parent both references each other
    P.S: NOT to be used independantly as is, should use the 'Tree' class as the interface
    '''

    value:  Optional[CT] = None
    parent: Optional['BST_Node'] = field(default=None, repr=False, compare=False)
    left:   Optional['BST_Node'] = field(default=None, repr=False, compare=False)
    right:  Optional['BST_Node'] = field(default=None, repr=False, compare=False)

    @property
    def grandparent(self) -> Union['BST_Node', bool]:
        '''get the parent of the parent of the node, if any'''
        try:
            return self.parent.parent
        except AttributeError:
            return None


    @property
    def uncle(self) -> Union['BST_Node', bool]:
        '''get the uncle of the parent of the node, if any'''
        try:
            # in case the node calling this has been deleted
            if self.grandparent.left == None: 
                return self.grandparent.right
            elif self.grandparent.right == None: 
                return self.grandparent.left

            return self.grandparent.right if self.parent is self.grandparent.left else self.grandparent.left
        except AttributeError:
            return None


    @property
    def sibling(self) -> Union['BST_Node', bool]:
        '''get the sibling of the node, if any'''
        try:
            # in case the node calling this has been deleted
            if self.parent.left == None: 
                return self.parent.right
            elif self.parent.right == None: 
                return self.parent.left

            return self.parent.left if self is self.parent.right else self.parent.right
        except AttributeError:
            return None
        

    def traverse(self, key: str='in', node: bool=True) -> List['BST_Node']:
        '''
        returns a list containing all the items in the binary tree in the given order type
        in-order  ['in']: from min-to-max
        pre-order ['pre']: root node as the beginning, from left to right, kinda like DFS
        post-order ['post']: root node as the end, from left to right
        level-order ['lvl']: from top-to-bottom, left-to-right, kinda like BST
        '''
        def inorder_traversal(node: 'BST_Node', path: list) -> List['BST_Node']:
            if node.left:
                inorder_traversal(node.left, path)
            path.append(node)
            if node.right:
                inorder_traversal(node.right, path)
            return path

        def postorder_traversal(node: 'BST_Node', path: list) -> List['BST_Node']:
            if node.left:
                postorder_traversal(node.left, path)
            if node.right:
                postorder_traversal(node.right, path)
            path.append(node)
            return path

        def preorder_traversal(node: 'BST_Node', path: list) -> List['BST_Node']:
            path.append(node)
            if node.left:
                preorder_traversal(node.left, path)
            if node.right:
                preorder_traversal(node.right, path)
            return path

        def levelorder_traversal(node: 'BST_Node', path: list) -> List['BST_Node']:
            from collections import deque

            stack = deque([node])

            while stack != deque([]):
                node = stack.popleft()
                path.append(node)

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

        all_nodes = traversing_option[key](self, [])

        if node: 
            return all_nodes

        return [node.value for node in all_nodes]


    def insert(self, value: CT) -> None:
        '''insert a value into the binary tree'''
        if self.value is None:  
            self.value = value
            return 
        self._insert(value)


    def _insert(self, value: CT) -> Union[None, 'BST_Node']:
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


    def find(self, value: CT) -> Union[None, 'BST_Node']:
        '''search for the given value in the binary tree'''
        if self.value == value: 
            return self
        if value < self.value and self.left != None:
            return self.left.find(value)
        elif value > self.value and self.right != None:
            return self.right.find(value)
        return None


    def find_min(self) -> 'BST_Node':
        '''find the minimum value relative to a specific node in the binary tree'''
        if self.left is None:
            return self
        return self.left.find_min()     


    def find_max(self) -> 'BST_Node':
        '''find the maximum value relative to a specific node in the binary tree'''
        if self.right is None:
            return self
        return self.right.find_max() 


    def find_lt(self, value: CT) -> 'BST_Node':
        '''find the node with the closest value that's less than the given value'''
        filtered_nodes = filter(lambda node: node.value < value, self.traverse(node=True))
        return min(filtered_nodes, key=lambda node: abs(value - node.value))


    def find_gt(self, value: CT) -> 'BST_Node':
        '''find the node with the closest value that's greater than the given value'''
        filtered_nodes = filter(lambda node: node.value > value, self.traverse(node=True))
        return min(filtered_nodes, key=lambda node: abs(value - node.value))


    def delete(self, value: CT) -> None:
        '''remove the given vaue from the binary tree'''

        node_to_delete = self.find(value)
        
        if node_to_delete is None:
            raise ValueError(f'{value} is not in {self.__class__.__name__}')

        node_to_delete._delete_node()   


    def _delete_node(self) -> 'BST_Node': 
        '''
        recursively going down the chain of nodes until a node with only 1 child or no child is found
        then, perform necceesarily steps to make the node obselete (set to None)

         CASE 1: if the node have 0 child
          
          if the node is not the root node, check the role of the node(right child/left child)
          --> then, destroy the node's relationship with its parent
          if the node is the root node, set its value to None
        __________________________________________________________________________________________________________________________
         CASE 2: if the node have 2 child
         
          --> get the child with the minimum value relative to the right child / 
              get the child with the maximum value relative to the left child 
              and recursively going down the chain from that child's position until a succesful deletion
        
          this will ensure that the chosen child fits the parent's position (doesn't violate any BST invariants), because
            - if the child is the one with the maximum value relative to the left child
              - replacing the parent with its value guarentees that all the child that's on the left 
                has 'smaller' value than 'him' and all the child on the right has bigger value than him
                [otherwise there's something wrong with the insertion to begin with]
        
            * Vice versa for the other case (if the child is the one with the minimum value relative to the right child)
        
         NOTE TO SELF:
         consider the following example:
         - the node to be deleted is the root node [7]
        
           - the successor node in this case would be [8], 
             since it is the one with the minimum value relative to the right child of the root node
        
             - [8] will be 'promoted' as the new root node / swap its value with the node to be deleted
        
               (This essentially 'deletes' the node since it has its original value replaced, 
                even though that the underlying object of the node is still the same 
                {i.e no new node has been created in the process})
               
               - the < _delete_node > function will then be called upon the original [8] node, 
                 in which the CASE 3 will be activated since there only ever will be at most 1 child for [8]
                 or else [8] wouldn't have been the minimum node 
                    7
                 /      \
                3        9
              /   \n    /  \
             1     5   8    10 
            / \n  / \n  \
           0   2 4   6   8.5
                      
                         
                    8
                 /      \
                3        9
              /   \n    /  \
             1     5   8.5  10 
            / \n  / \n 
           0   2 4   6 
        
        __________________________________________________________________________________________________________________________

         CASE 3: if the node only have 1 child
         
          --> check the child's relationship with the node
        
              if the node has a parent (i.e not the root node),
          ----> then, create a parent-child relationship between the node's parent and the child
                with respect to the child's relationship with the node (right child/left child)
        
              if the node does not have a parent (i.e is a root node)
          ----> then, swap entires with the child node
         '''

        # CASE 1: node have 0 child
        if self.left is None and self.right is None:
            if self.parent != None:
                if self.parent.left == self:
                    self.parent.left = None
                else:
                    self.parent.right = None
            else:
                self.value = None

            return self

        # CASE 2: node have 2 child
        elif self.left and self.right:
            successor_node = self.right.find_min()
            self.value = successor_node.value 
            return successor_node._delete_node()

        # CASE 3: node has 1 child 
        else:
            child_node = self.left if self.left != None else self.right

            # if the node is not the root node
            if self.parent != None:

                # rewire the relationship 
                child_node.parent = self.parent
                if self.parent.left == self:
                    self.parent.left = child_node
                else:
                    self.parent.right = child_node

            # if the node is the root node
            else:

                # swap identity with the child node
                self.__dict__ = child_node.__dict__
                if child_node.right != None:
                    child_node.right.parent = self
                if child_node.left != None:
                    child_node.left.parent = self
                
                # get rid of the cyclic reference after the identity swap
                self.parent = None
            
            return child_node


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
                

@dataclass
class Splay_Node(BST_Node):
    '''
    - the node class for the splay tree
    - self-adjusting, recently searched/inserted/deleted node will be moved to the top for faster access
    - for internal use only, shouldn't be used independently
    '''


    def _update(self) -> Node:
        '''
        internal function for the splay tree's node
        recursively move the intended node up until it is the root node
        '''
        if self.parent == None: 
            return self

        if self == self.parent.right:   
            self.parent._rotate_left()

        elif self == self.parent.left:
            self.parent._rotate_right()

        return self._update()


    def insert(self, value: CT) -> Union[None, 'BST_Node']:
        '''
        add a node with the given value into the tree
        update/splay the node to the root upon a succesfully insert
        returns a node to be designated as the 'root node' if the value is succesfully inserted
        '''
        new_node = self._insert(value)

        if not new_node: return None

        return new_node._update()


    def delete(self, value: CT) -> Union[None, 'BST_Node']:
        '''
        remove the node that contains the specified value from the tree
        update/splay the parent of the deleted node to the root upon a succesfully delete
        returns a node to be designated as the 'root node' if the value is succesfully deleted
        '''
        node_to_delete = self.find(value) 

        if node_to_delete == None:
            raise ValueError(f'{value} is not in {self.__class__.__name__}')

        node_to_splay = node_to_delete.parent 

        node_to_delete._delete_node()

        return node_to_splay._update() if node_to_splay != None else None
