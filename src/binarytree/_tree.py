from operator import attrgetter
from types import MethodType
from ._type_hint import *


class Tree(Generic[CT]):
    '''
    - This is the base class for all binary search tree 
    - it acts as an interface for the node classes
      and shouldn't be instantiated on its own
    
    all binary search tree variations should inherit this class 
    to obtain all the necessary interface functions
    '''
    _node_type: Node = None


    def __init__(self, key=None):
        self.root = None

        if self._node_type is None:
            raise TypeError("Cannot instantiate abstract class.")


    @property
    def isempty(self):
        return self.root == None


    @property
    def dtype(self):
        '''returns the data type of that a tree contains'''
        return type(self.root.value)
    

    @property
    def height(self) -> int:
        '''recursively get the height of the tree '''
        def traversal_counter(node) -> int:
            if node is None:
                return -1
            return 1 + max(traversal_counter(node.left), traversal_counter(node.right))

        return traversal_counter(self.root) 


    @property
    def iscomplete(self) -> bool:
        '''
        check whether the tree is complete,
        -> i.e all nodes of the tree either has 2 child or no child
        '''
        def traversal_check(node) -> bool:
            # keep going down the chain of nodes 
            # until the leftmost/rightmost node has been reached
            # then, return True, as leaf nodes has no child nodes 
            if node is None: return True

            left_check  = traversal_check(node.left)
            right_check = traversal_check(node.right)
            
            # check whether the node is 'complete'
            # i.e: whether is has both child or no child
            completeness_check = (node.left != None and node.right != None) or \
                                 (node.left == None and node.right == None)

            return left_check and right_check and completeness_check

        return traversal_check(self.root)        


    @property
    def isperfect(self) -> bool:
        '''
        check whether the tree is perfect
        -> i.e each branch of the tree has the same height
        '''
        def traversal_check(node) -> Tuple[bool, int]:
            # keep going down the chain of nodes 
            # until the leftmost/rightmost node has been reached
            # then, return True, as leaf nodes has no child nodes and are inherently balanced
            if node is None: return (True, -1)

            left_height  = traversal_check(node.left)
            right_height = traversal_check(node.right)
            
            # check whether the left & right node is perfect
            # and whether the height the node is perfect
            perfectness_check = (left_height[0] and right_height[0] and abs(left_height[1] - right_height[1]) == 0)

            # return the 'perfectness_check' variable and the height of the current node
            return (perfectness_check, 1 + max(left_height[1], right_height[1]))

        return traversal_check(self.root)[0]    


    @property
    def isbinary(self) -> bool:
        '''
        check whether the tree obeys the binary search tree's invariant
        i.e:
        - left node's value < node's value 
        - right node's value > node's value
        '''
        def traversal_check(node) -> bool:
            # keep going down the chain of nodes 
            # until the leftmost/rightmost node has been reached
            # then, return True, as leaf nodes has no child nodes 
            if node is None: return True

            left_check  = traversal_check(node.left)
            right_check = traversal_check(node.right)
            
            # check whether the left & right node obey the BST invariant
            check_binary = left_check and right_check

            # then, check the node itself, whether it obeys the BST invariant
            if node.left != None and node.left > node: 
                check_binary = False
            if node.right != None and node.right < node: 
                check_binary = False

            return check_binary

        return traversal_check(self.root)


    @property
    def isbalanced(self) -> bool:
        '''
        check whether the tree is balanced, i.e both side of the tree, 
        left & right have similar/same number of nodes
        -> the difference in number of nodes for both side 
           of every node does not exceed 1

        STEPS:

            1. go down until the leftmost & rightmost node has been reached
            2. start checking whether each node is balanced
            3. return their height along with whether they're balanced or not 
            4. unfold the recursion to the previous node
            5. rinse & repeat until the recursion unfolds back to the starting node/root node

            * so, if any one of the node, starting from the leaf nodes, is unbalanced
              it will cause will the other nodes 'above' him to be unbalanced as well
              due to all to them depending on the last node's balance_value(boolean)
            
            * basically, only 2 value is passed around, 
              the balance_value & the height of the node
              - the balance_value is required for the said chain reaction
              - while the node's height is required for the checking
        '''
        def traversal_check(node) -> Tuple[bool, int]:
            # keep going down the chain of nodes 
            # until the leftmost/rightmost node has been reached
            # then, return True, as leaf nodes has no child nodes and are inherently balanced
            # + the height of the leaf node, which is -1 since again, it has no child 
            if node is None: return (True, -1)

            left_height  = traversal_check(node.left)
            right_height = traversal_check(node.right)
            
            # check whether the left & right node is balanced
            # and whether the height the node is balanced
            balanced = (left_height[0] and right_height[0] and abs(left_height[1] - right_height[1]) <= 1)

            # return the 'balanced' variable and the height of the current node
            return (balanced, 1 + max(left_height[1], right_height[1]))

        return traversal_check(self.root)[0]


    @classmethod
    def fill_tree(cls, values: List[CT]) -> 'Tree':
        '''generates a binary tree with all the values from a list'''
        new_bst = cls()
        for value in values:
            new_bst.insert(value)
        return new_bst


    def insert(self, value: CT) -> None:
        '''add a node with the given value into the tree'''
        if self.root == None:
            self.root = self._node_type(value)
            return
            
        new_root = self.root.insert(value)

        if new_root != None:
            self.root = new_root


    def delete(self, value: CT) -> None:
        '''remove the node that contains the specified value from the tree'''
        node_to_delete = self.root.find(value)

        if node_to_delete == None:
            raise ValueError(f'{value} is not in {self.__class__.__name__}')

        # if the root's left and right subtree is both empty
        # the node that needs to be deleted must be the root node
        # since there's nothing left in the tree to swap the entires with, 
        # just set the value of the root node to None
        if self.root.left is None and self.root.right is None:
            self.root = None
            return 

        new_root = self.root.delete(node_to_delete)
        if new_root != None:
            self.root = new_root


    def traverse(self, key: str='in', node: bool=False) -> List[Union[Node, CT]]:
        '''
        returns a list containing all the items in the binary tree in the given order type
        in-order  ['in']: from min-to-max
        pre-order ['pre']: root node as the beginning, from left to right, kinda like DFS
        post-order ['post']: root node as the end, from left to right
        level-order ['lvl']: from top-to-bottom, left-to-right, kinda like BST
        '''
        return self.root.traverse(key, node)


    def find(self, value: CT, node: bool=False) -> Union[Node, CT]:
        '''get the node with the given value'''
        target_node = self.root.find(value)
        if target_node:
            return target_node.value if not node else target_node

    def find_lt(self, value: CT, node: bool=False) -> Union[Node, CT]:
        '''get the node with the given value'''
        target_node = self.root.find_lt(value)
        if target_node:
            return target_node.value if not node else target_node 


    def find_gt(self, value: CT, node: bool=False) -> Union[Node, CT]:
        '''find the node with the closest value that's less than the given value'''
        target_node = self.root.find_gt(value)
        if target_node:
            return target_node.value if not node else target_node 


    def find_le(self, value: CT, node: bool=False) -> Union[Node, CT]:
        '''get the node with the given value'''
        target_node = self.root.find_le(value)
        if target_node:
            return target_node.value if not node else target_node 


    def find_ge(self, value: CT, node: bool=False) -> Union[Node, CT]:
        '''find the node with the closest value that's less than the given value'''
        target_node = self.root.find_ge(value)
        if target_node:
            return target_node.value if not node else target_node


    def find_max(self, node: bool=False) -> Union[Node, CT]:
        '''get the node with the maximum value in the tree'''
        target_node = self.root.find_max()
        if target_node:
            return target_node.value if not node else target_node


    def find_min(self, node: bool=False) -> Union[Node, CT]:
        '''get the node with the minimum value in the tree'''
        target_node = self.root.find_min()
        if target_node:
            return target_node.value if not node else target_node


    def pop(self, value: CT=None, key: str='val') -> CT:
        '''get and delete the given value from the tree'''
        popping_options = {
        'val': self.find,
        'min': self.find_min,
        'max': self.find_max
        }

        if key not in popping_options:
            raise ValueError(f'{key} given is not a valid option')

        if (key != 'val' and value != None) or (key == 'val' and value == None):
            raise ValueError(f'only one of the arguements can be given')

        found_val = popping_options[key](value) if key == 'val' else popping_options[key]()

        self.delete(found_val)

        return found_val

    def __add__(self, other: Union[CT, 'Tree']) -> 'Tree':
        '''add this tree to another tree, omitting all repeated values'''
        if isinstance(other, type(self)):
            if other.root == None or self.root == None: 
                if other.root != None:
                    return type(self).fill_tree(other.traverse())
                elif self.root != None:
                    return type(self).fill_tree(self.traverse())
                else:
                    return type(self)()
            if self.dtype != other.dtype:
                raise TypeError(f"cannot add '{type(self).__name__}({self.dtype.__name__})' with '{type(other).__name__}({other.dtype.__name__})'")
            self_vals = self.traverse()
            other_vals = other.traverse()
            total_vals = [val for val in other_vals if val not in self_vals] + self_vals
            return type(self).fill_tree(total_vals)

        try:
            return type(self).fill_tree(self.traverse()).insert(other)
        except TypeError:
            raise TypeError(f"cannot insert value of type '{other.__class__.__name__}' into '{self.__class__.__name__}({self.dtype.__name__})'")


    def __iadd__(self, other: Union[CT, 'Tree']) -> 'Tree':
        '''add this tree to another tree, omitting all repeated values'''
        if isinstance(other, type(self)):
            if other.root == None or self.root == None: 
                if self.root != None:
                    return self
                else:
                    for node in other:
                        self.insert(node.value)
                    return self
            if self.dtype != other.dtype:
                raise TypeError(f"cannot add '{type(self).__name__}({self.dtype.__name__})' with '{type(other).__name__}({other.dtype.__name__})'")
            self_vals = self.traverse()
            other_vals = other.traverse()
            for val in other_vals:
                if val not in self_vals:
                    self.insert(val)
            return self

        try:
            self.insert(other)
            return self
        except TypeError:
            raise TypeError(f"cannot insert value of type '{other.__class__.__name__}' into '{self.__class__.__name__}({self.dtype.__name__})'")


    def __sub__(self, other: Union[CT, 'Tree']) -> 'Tree':
        '''
        subtract this tree by another tree
        - only common values within both trees will be removed 
        '''
        if isinstance(other, type(self)):
            if other.root == None or self.root == None: 
                if self.root != None:
                    return type(self).fill_tree(self.traverse())
                else:
                    return type(self)()
            if self.dtype != other.dtype:
                raise TypeError(f"cannot subtract {type(self).__name__}('{self.dtype.__name__}') from '{type(other).__name__}({other.dtype.__name__})'")
            self_vals = self.traverse()
            other_vals = other.traverse()
            total_vals = [val for val in self_vals if val not in other_vals]
            return type(self).fill_tree(total_vals)

        try:
            return type(self).fill_tree(self.traverse()).delete(other)
        except TypeError:
            raise TypeError(f"cannot delete value of type '{other.__class__.__name__}' from '{self.__class__.__name__}({self.dtype.__name__})'")


    def __isub__(self, other: Union[CT, 'Tree']) -> 'Tree':
        '''
        subtract this tree by another tree
        - only common values within both trees will be removed 
        '''
        if isinstance(other, type(self)):
            if other.root == None or self.root == None: return self
            if self.dtype != other.dtype:
                raise TypeError(f"cannot subtract {type(self).__name__}('{self.dtype.__name__}') from '{type(other).__name__}({other.dtype.__name__})'")
            self_vals = self.traverse()
            other_vals = other.traverse()
            for val in other_vals:
                if val in self_vals:
                    self.delete(val)
            return self
        
        try:
            self.insert(other)
            return self
        except TypeError:
            raise TypeError(f"cannot delete value of type '{other.__class__.__name__}' from '{self.__class__.__name__}({self.dtype.__name__})'")


    def __getattribute__(self, attr_name):
        attr = super().__getattribute__(attr_name)

        if isinstance(attr, MethodType) and attr_name not in ['delete', 'insert']:
            def root_checker(*args, **kwargs):
                if self.root == None:
                    return None
                result = attr(*args, **kwargs)
                return result
            return root_checker
        else:
            return attr


    def __getitem__(self, key):
        return self.root.find(key)


    def __setitem__(self, key, value):
        self.delete(key)
        self.insert(value)


    def __delitem__(self, key):
        self.delete(key)


    def __len__(self):
        return len(self.traverse())


    def __iter__(self):
        all_nodes = self.traverse(node=True)
        return iter((all_nodes)) if all_nodes else iter([])


    def __contains__(self, value: CT) -> bool:
        return self.root.find(value) != None


    def __str__(self):
        return str(self.traverse())
