from typing import Generic, Union, Tuple, List
from types import MethodType

from ._type_hint import CT, N, Node


class BinaryTree(Generic[CT]):
    '''
    - This is the base class for all binary search tree
    - it acts as an interface for the node classes
      and shouldn't be instantiated on its own

    all binary search tree variations should inherit this class
    to obtain all the necessary interface functions
    '''
    _node_type: N = None

    def __init__(self):
        if self._node_type is None:
            raise TypeError("Cannot instantiate base class.")

        self.root = self._node_type()
        self._size = 0

    @property
    def dtype(self):
        '''returns the data type of that a tree contains'''
        if self.root is None:
            return None
        return type(self.root.value)

    @property
    def height(self) -> int:
        '''recursively get the height of the tree '''

        def traversal_counter(node) -> int:
            if node is None:
                return -1
            return 1 + max(traversal_counter(node.left),
                           traversal_counter(node.right))

        return traversal_counter(self.root)

    @property
    def is_complete(self) -> bool:
        '''
        check whether the tree is complete,
        -> i.e all nodes of the tree either has 2 child or no child
        '''

        def traversal_check(node) -> bool:
            # keep going down the chain of nodes
            # until the leftmost/rightmost node has been reached
            # then, return True, as leaf nodes has no child nodes
            if node is None:
                return True

            left_check = traversal_check(node.left)
            right_check = traversal_check(node.right)

            # check whether the node is 'complete'
            # i.e: whether is has both child or no child
            completeness_check = (node.left and node.right) or \
                                 (node.left is None and node.right is None)

            return left_check and right_check and completeness_check

        return traversal_check(self.root)

    @property
    def is_perfect(self) -> bool:
        '''
        check whether the tree is perfect
        -> i.e each branch of the tree has the same height
        '''

        def traversal_check(node) -> Tuple[bool, int]:
            # keep going down the chain of nodes
            # until the leftmost/rightmost node has been reached
            # return True, as leaf nodes has 0 child and are balanced
            if node is None:
                return (True, -1)

            left_check = traversal_check(node.left)
            right_check = traversal_check(node.right)

            # check whether the left & right node is perfect
            # and whether the height the node is perfect
            perfectness_check = (left_check[0] and right_check[0]
                                 and abs(left_check[1] - right_check[1]) == 0)

            return (perfectness_check, 1 + max(left_check[1], right_check[1]))

        return traversal_check(self.root)[0]

    @property
    def is_binary(self) -> bool:
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
            if node is None:
                return True

            left_check = traversal_check(node.left)
            right_check = traversal_check(node.right)

            # check whether the left & right node obey the BST invariant
            check_binary = left_check and right_check

            # then, check the node itself, whether it obeys the BST invariant
            if node.left and node.left >= node:
                check_binary = False
            if node.right and node.right < node:
                check_binary = False

            return check_binary

        return traversal_check(self.root)

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
            4. unfold the recursion to the prev node
            5. rinse & repeat until the recursion unfolds
               back to the starting node/root node

            * so, if any one of the node, starting from the leaf nodes,
            is unbalanced it will cause will the other nodes 'above'
            him to be unbalanced as well due to all to them depending on
            the last node's balance_value(boolean)

            * basically, only 2 value is passed around,
              the balance_value & the height of the node
              - the balance_value is required for the said chain reaction
              - while the node's height is required for the checking
        '''

        def traversal_check(node) -> Tuple[bool, int]:
            # keep going down the chain of nodes
            # until the leftmost/rightmost node has been reached
            # return True, as leaf nodes has no child nodes and are balanced
            # + the height of the leaf node, which is -1 since it has no child
            if node is None:
                return (True, -1)

            left_height = traversal_check(node.left)
            right_height = traversal_check(node.right)

            # check whether the left & right node is balanced
            # and whether the height the node is balanced
            balanced = (left_height[0] and right_height[0]
                        and abs(left_height[1] - right_height[1]) <= 1)

            # return the 'balanced' variable and the height of the current node
            return (balanced, 1 + max(left_height[1], right_height[1]))

        return traversal_check(self.root)[0]

    @classmethod
    def fill_tree(cls, values: List[CT]) -> 'BinaryTree':
        '''generates a binary tree with all the values from a list'''
        new_bst = cls()
        for value in values:
            new_bst.insert(value)
        return new_bst

    def insert(self, value: CT) -> None:
        '''add a node with the given value into the tree'''
        if self.root.value is None:
            self.root.value = value

        else:
            new_root = self.root.insert_node(value)
            if new_root:
                self.root = new_root

        self._size += 1

    def delete(self, value: CT) -> None:
        '''remove the node that contains the specified value from the tree'''
        if self.root.value is None:
            raise ValueError(f'{value} is not in {self.__class__.__name__}')

        node_to_delete = self.root.find_node(value)

        if node_to_delete is None:
            raise ValueError(f'{value} is not in {self.__class__.__name__}')

        new_root = self.root.delete_node(node_to_delete)

        if new_root:
            self.root = new_root

        self._size -= 1

    def pop(self, value: CT = None, key: str = None) -> CT:
        '''get and delete the given value from the tree'''
        popping_options = {
            'val': self.find,
            'min': self.find_min,
            'max': self.find_max
        }

        if self.root.value is None:
            raise IndexError(
                f'trying to pop from an empty {type(self).__name__} tree')

        if key and key not in popping_options:
            raise ValueError(f'{key} given is not a valid option')

        if key and value:
            raise ValueError('only one of the arguements can be given')

        # default settings for the pop method
        popping_func = popping_options['min']

        if value:
            popping_func = lambda: popping_options['val'](value)  # noqa: E731
        if key:
            popping_func = popping_options[key]

        found_val = popping_func()

        self.delete(found_val)

        return found_val

    def clear(self) -> None:
        self.root.left = None
        self.root.right = None
        self.root.value = None

    def traverse(self,
                 key: str = 'in',
                 node: bool = False) -> List[Union[Node, CT]]:
        '''
        returns list of all the items in the tree in the given order type
        in-order  ['in']: from min-to-max
        pre-order ['pre']: root node as the beginning, from left to right
        post-order ['post']: root node as the end, from left to right
        level-order ['lvl']: from top-to-bottom, left-to-right, kinda like BST
        '''
        if self.root.value is None:
            return []
        return self.root.traverse_node(key, node)

    def find(self, value: CT, node: bool = False) -> Union[Node, CT]:
        '''get the node with the given value'''
        target_node = self.root.find_node(value)
        if target_node:
            return target_node.value if not node else target_node

    def find_lt(self,
                value: CT,
                node: bool = False,
                **kwargs) -> Union[Node, CT]:
        '''get the node with the given value'''
        target_node = self.root.find_lt_node(value, **kwargs)
        if target_node:
            return target_node.value if not node else target_node

    def find_gt(self,
                value: CT,
                node: bool = False,
                **kwargs) -> Union[Node, CT]:
        '''find the node with the closest value that's > the given value'''
        target_node = self.root.find_gt_node(value, **kwargs)
        if target_node:
            return target_node.value if not node else target_node

    def find_le(self,
                value: CT,
                node: bool = False,
                **kwargs) -> Union[Node, CT]:
        '''get the node with the given value'''
        target_node = self.root.find_le_node(value, **kwargs)
        if target_node:
            return target_node.value if not node else target_node

    def find_ge(self,
                value: CT,
                node: bool = False,
                **kwargs) -> Union[Node, CT]:
        '''find the node with the closest value that's < the given value'''
        target_node = self.root.find_ge_node(value, **kwargs)
        if target_node:
            return target_node.value if not node else target_node

    def find_max(self, node: bool = False, **kwargs) -> Union[Node, CT]:
        '''get the node with the maximum value in the tree'''
        target_node = self.root.find_max_node(**kwargs)
        if target_node:
            return target_node.value if not node else target_node

    def find_min(self, node: bool = False, **kwargs) -> Union[Node, CT]:
        '''get the node with the minimum value in the tree'''
        target_node = self.root.find_min_node(**kwargs)
        if target_node:
            return target_node.value if not node else target_node

    def __add__(self, other: Union[CT, 'BinaryTree']) -> 'BinaryTree':
        '''add this tree to another tree, omitting all repeated values'''
        if isinstance(other, type(self)):
            if self.dtype != other.dtype and not isinstance(
                    self.root.value, type(None)) and not isinstance(
                        other.root.value, type(None)):
                raise TypeError(
                    f"cannot add '{type(self).__name__}({self.dtype.__name__})' \
                      with '{type(other).__name__}({other.dtype.__name__})'")
            return type(self).fill_tree([val for val in self] +
                                        [val for val in other])

        try:
            return type(self).fill_tree(self.traverse()).insert(other)
        except TypeError:
            raise TypeError(
                f"cannot insert value of type '{other.__class__.__name__}' \
                  into '{self.__class__.__name__}({self.dtype.__name__})'")

    def __iadd__(self, other: Union[CT, 'BinaryTree']) -> 'BinaryTree':
        '''add this tree to another tree, omitting all repeated values'''
        if isinstance(other, type(self)):
            if self.dtype != other.dtype and not isinstance(
                    self.root.value, type(None)) and not isinstance(
                        other.root.value, type(None)):
                raise TypeError(
                    f"cannot add '{type(self).__name__}({self.dtype.__name__})' \
                      with '{type(other).__name__}({other.dtype.__name__})'")
            [self.insert(val) for val in other]
            return self

        try:
            self.insert(other)
            return self
        except TypeError:
            raise TypeError(
                f"cannot insert value of type '{other.__class__.__name__}' into \
                '{self.__class__.__name__}({self.dtype.__name__})'")

    def __sub__(self, other: Union[CT, 'BinaryTree']) -> 'BinaryTree':
        '''
        subtract this tree by another tree
        - only common values within both trees will be removed
        '''
        if isinstance(other, type(self)):
            if self.dtype != other.dtype and not isinstance(
                    self.root.value, type(None)) and not isinstance(
                        other.root.value, type(None)):
                raise TypeError(
                    f"cannot subtract {type(self).__name__}('{self.dtype.__name__}') from \
                      '{type(other).__name__}({other.dtype.__name__})'")
            return type(self).fill_tree(
                [val for val in self if val not in other])

        try:
            return type(self).fill_tree(self.traverse()).delete(other)
        except TypeError:
            raise TypeError(
                f"cannot delete value of type '{other.__class__.__name__}' from \
                '{self.__class__.__name__}({self.dtype.__name__})'")

    def __isub__(self, other: Union[CT, 'BinaryTree']) -> 'BinaryTree':
        '''
        subtract this tree by another tree
        - only common values within both trees will be removed
        '''
        if isinstance(other, type(self)):
            if self.dtype != other.dtype and not isinstance(
                    self.root.value, type(None)) and not isinstance(
                        other.root.value, type(None)):
                raise TypeError(
                    f"cannot subtract {type(self).__name__}('{self.dtype.__name__}') \
                    from '{type(other).__name__}({other.dtype.__name__})'")

            [self.delete(val) for val in other if val in self]
            return self

        try:
            self.delete(other)
            return self
        except TypeError:
            raise TypeError(
                f"cannot delete value of type '{other.__class__.__name__}' \
                from '{self.__class__.__name__}({self.dtype.__name__})'")

    def __getattribute__(self, attr_name):
        attr = super().__getattribute__(attr_name)

        methods_with_empty_root_handler = [
            'pop', 'traverse', 'insert', 'delete', 'clear'
        ]

        if isinstance(attr, MethodType
                      ) and attr_name not in methods_with_empty_root_handler:

            def root_checker(*args, **kwargs):
                if self.root.value is None:
                    return None
                retval = attr(*args, **kwargs)
                return retval

            return root_checker

        return attr

    def __setattr__(self, attr_name, val):
        if attr_name == '_node_type':
            raise ValueError(f'{attr_name} of the tree cannot be altered!')
        super().__setattr__(attr_name, val)

    def __getitem__(self, key):
        mod_key = len(self) - abs(key) if key < 0 else key

        if mod_key > len(self) - 1 or mod_key < 0:
            raise IndexError(f'{key} is out of range!')

        return self.traverse()[mod_key]

    def __setitem__(self, key, value):
        self.delete(self[key])
        self.insert(value)

    def __delitem__(self, key):
        self.delete(self[key])

    def __len__(self):
        return self._size

    def __iter__(self):
        yield from self.traverse()

    def __contains__(self, value: CT) -> bool:
        if self.root.value is None:
            return False
        return self.root.find_node(value)

    def __bool__(self) -> bool:
        return self.root.value

    def __str__(self):
        return str(self.traverse())
