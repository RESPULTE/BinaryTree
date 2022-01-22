from typing import Any, Protocol, TypeVar


class ComparableType(Protocol):

    def __lt__(self, other: Any) -> bool:
        ...

    def __le__(self, other: Any) -> bool:
        ...

    def __gt__(self, other: Any) -> bool:
        ...

    def __ge__(self, other: Any) -> bool:
        ...


CT = TypeVar('CT', bound=ComparableType)


class BinaryNode(Protocol):

    value: Any
    left: 'BinaryNode'
    right: 'BinaryNode'
    parent: 'BinaryNode'

    def insert_node(self, value):
        ...

    def delete_node(self, value):
        ...

    def traverse_node(self, key):
        ...

    def find_node(self, value):
        ...


BN = TypeVar('BN', bound=BinaryNode)


class Tree(Protocol):

    _node_type: BN

    def insert(self, value):
        ...

    def delete(self, value):
        ...

    def traverse(self, key):
        ...

    def find(self, value):
        ...


Tree = TypeVar('BST', bound=Tree)
