from typing import Optional, Protocol, TypeVar, Union, List

T = TypeVar('T')
N = TypeVar('N')


class Tree(Protocol):

    root: N
    _size: int

    @property
    def dtype(self):
        '''returns the data type of that a tree contains'''
        pass

    @property
    def size(self):
        '''returns the data type of that a tree contains'''
        pass

    @classmethod
    def fill_tree(cls, values: List[T]) -> 'Tree':
        '''generates a binary tree with all the values from a list'''
        pass

    def extend(self, values: List[T]) -> None:
        pass

    def insert(self, value: T) -> None:
        '''add a node with the given value into the tree'''
        pass

    def delete(self, value: T) -> None:
        '''remove the node that contains the specified value from the tree'''
        pass

    def pop(self, value: T = None, key: str = None) -> T:
        '''get and delete the given value from the tree'''
        pass

    def clear(self) -> None:
        pass

    def traverse(self, key: str = 'in', node: Optional[bool] = False) -> List[Union[N, T]]:
        pass

    def find(self, value: T, node: Optional[bool] = False) -> Union[N, T]:
        '''get the node with the given value'''
        pass

    def find_lt(self, value: T, node: Optional[bool] = False) -> Union[N, T]:
        '''get the node with the given value'''
        pass

    def find_gt(self, value: T, node: Optional[bool] = False) -> Union[N, T]:
        '''find the node with the closest value that's > the given value'''
        pass

    def find_le(self, value: T, node: Optional[bool] = False) -> Union[N, T]:
        '''get the node with the given value'''
        pass

    def find_ge(self, value: T, node: Optional[bool] = False) -> Union[N, T]:
        '''find the node with the closest value that's < the given value'''
        pass

    def find_max(self, node: Optional[bool] = False) -> Union[N, T]:
        '''get the node with the maximum value in the tree'''
        pass

    def find_min(self, node: Optional[bool] = False) -> Union[N, T]:
        '''get the node with the minimum value in the tree'''
        pass

    def pickle(self, filename: Optional[str] = None) -> None:
        pass

    def __add__(self, other: Union[T, 'Tree']) -> 'Tree':
        '''add this tree to another tree, omitting all repeated values'''
        pass

    def __iadd__(self, other: Union[T, 'Tree']) -> 'Tree':
        '''add this tree to another tree, omitting all repeated values'''
        pass

    def __sub__(self, other: Union[T, 'Tree']) -> 'Tree':
        '''
        subtraT this tree by another tree
        - only common values within both trees will be removed
        '''
        pass

    def __isub__(self, other: Union[T, 'Tree']) -> 'Tree':
        '''
        subtraT this tree by another tree
        - only common values within both trees will be removed
        '''
        pass

    def __len__(self):
        pass

    def __iter__(self):
        pass

    def __contains__(self, value: T) -> bool:
        pass

    def __bool__(self) -> bool:
        pass

    def __str__(self):
        pass
