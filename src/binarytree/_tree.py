from ._type_hint import *


class Tree(Generic[CT]):
    '''
    - This is the base class for all binary search tree 
    - it acts as an interface for the node classes
      and shouldn't be instantiated on its own
    
    all binary search tree variations should inherit this class 
    to obtain all the necessary interface functions
    '''
    _node_type = None


    def __init__(self):
        self.root = None

        if self._node_type is None:
            raise TypeError("Cannot instantiate abstract class.")


    @property
    def dtype(self):
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
    def is_balanced(self) -> bool:
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
            balanced = (left_height[0] and right_height[0] and
                        abs(left_height[1] - right_height[1]) <= 1)

            # return the 'balanced' variable and the height of the current node
            # to be used for the previous node
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
        new_root = self.root.delete(value)
        if new_root != None:
            self.root = new_root


    def traverse(self, key: str='in', value: bool=True) -> List[Node]:
        '''
        returns a list containing all the items in the binary tree in the given order type
        in-order  ['in']: from min-to-max
        pre-order ['pre']: root node as the beginning, from left to right, kinda like DFS
        post-order ['post']: root node as the end, from left to right
        level-order ['lvl']: from top-to-bottom, left-to-right, kinda like BST
        '''
        return self.root.traverse(key, value)


    def find_node(self, value: CT) -> Node:
        '''
        get the node with the given value, 
        will raise an error if it doesnt belong in the tree
        '''
        return self.root.find(value)


    def find_closest_node(self, value: CT) -> Node:
        '''find the node with the closest value to the given value'''
        return self.root.find_closest(value)


    def find_max_node(self) -> Node:
        '''get the node with the maximum value in the tree'''
        return self.root.find_max()


    def find_min_node(self) -> Node:
        '''get the node with the minimum value in the tree'''
        return self.root.find_min()


    def __add__(self, other: Union[CT, 'Tree']) -> 'Tree':
        '''add this tree to another tree, omitting all repeated values'''
        if isinstance(other, type(self)):
            if self.dtype != other.dtype:
                raise TypeError(f"cannot add '{type(self).__name__}({self.dtype.__name__})' with '{type(other).__name__}({other.dtype.__name__})'")
            self_vals = self.traverse()
            other_vals = other.traverse()
            total_vals = [val for val in other_vals if val not in self_vals] + self_vals
            return self.fill_tree(total_vals)

        try:
            return self.fill_tree(self.traverse()).insert(other)
        except TypeError:
            raise TypeError(f"cannot insert value of type '{other.__class__.__name__}' into '{self.__class__.__name__}({self.dtype.__name__})'")


    def __iadd__(self, other: Union[CT, 'Tree']) -> 'Tree':
        '''add this tree to another tree, omitting all repeated values'''
        if isinstance(other, type(self)):
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
            if self.dtype != other.dtype:
                raise TypeError(f"cannot subtract {type(self).__name__}('{self.dtype.__name__}') from '{type(other).__name__}({other.dtype.__name__})'")
            self_vals = self.traverse()
            other_vals = other.traverse()
            total_vals = [val for val in self_vals if val not in other_vals]
            return self.fill_tree(total_vals)

        try:
            return self.fill_tree(self.traverse()).delete(other)
        except TypeError:
            raise TypeError(f"cannot delete value of type '{other.__class__.__name__}' from '{self.__class__.__name__}({self.dtype.__name__})'")



    def __isub__(self, other: Union[CT, 'Tree']) -> 'Tree':
        '''
        subtract this tree by another tree
        - only common values within both trees will be removed 
        '''
        if isinstance(other, type(self)):
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


    def __iter__(self):
        return iter((self.traverse()))


    def __contains__(self, value: CT) -> bool:
        return self.root.find(value) != None


    def __str__(self):
        return str(self.traverse())
