from typing import Protocol, Union, TypeVar


class ComparableType(Protocol):

    def __lt__(self, other: 'ComparableType') -> bool:
        ...

    def __le__(self, other: 'ComparableType') -> bool:
        ...

    def __gt__(self, other: 'ComparableType') -> bool:
        ...

    def __ge__(self, other: 'ComparableType') -> bool:
        ...


CT = TypeVar('CT', bound=ComparableType)


class BinarySearchNode(Protocol):

    value: CT
    left: 'BinarySearchNode'
    right: 'BinarySearchNode'
    parent: 'BinarySearchNode'

    @property
    def grandparent(self) -> Union['BinarySearchNode', None]:
        pass

    @property
    def uncle(self) -> Union['BinarySearchNode', None]:
        pass

    @property
    def sibling(self) -> Union['BinarySearchNode', None]:
        pass

    @property
    def depth(self) -> int:
        pass

    @property
    def height(self) -> int:
        pass

    @property
    def is_leaf(self) -> bool:
        pass

    @property
    def is_branch(self) -> bool:
        pass

    def insert_node(self, value: CT) -> None:
        pass

    def _insert_node(self, value: CT) -> Union[None, 'BinarySearchNode']:
        pass

    def find_node(self, value: CT) -> Union[None, 'BinarySearchNode']:
        pass

    def find_gt_node(self, value: CT) -> Union['BinarySearchNode', None]:
        pass

    def find_lt_node(self, value: CT) -> Union['BinarySearchNode', None]:
        pass

    def find_le_node(self, value: CT) -> Union['BinarySearchNode', None]:
        pass

    def find_ge_node(self, value: CT) -> Union['BinarySearchNode', None]:
        pass

    def find_min_node(self) -> 'BinarySearchNode':
        pass

    def find_max_node(self) -> 'BinarySearchNode':
        pass

    def delete_node(self, node_to_delete: 'BinarySearchNode') -> None:
        pass

    def _delete_node(self) -> 'BinarySearchNode':
        pass

    def _rotate_left(self) -> None:
        pass

    def _rotate_right(self) -> None:
        pass


BSN = TypeVar('BSN', bound=BinarySearchNode)
