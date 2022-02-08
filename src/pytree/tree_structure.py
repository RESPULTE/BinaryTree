from typing import Optional, Protocol, TypeVar, Union, List

T = TypeVar('T')
N = TypeVar('N')

# TODO: documentation


class Tree(Protocol):

    root: N

    @property
    def dtype(self):
        '''returns the data type of that a tree contains'''
        pass

    @property
    def height(self):
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

    def clear(self) -> None:
        pass

    def traverse(self, key: str = 'in', node: Optional[bool] = False) -> List[Union[N, T]]:
        pass

    def find(self, value: T, node: Optional[bool] = False) -> Union[N, T]:
        '''get the node with the given value'''
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
