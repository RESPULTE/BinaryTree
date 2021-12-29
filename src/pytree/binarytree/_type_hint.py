from typing import Any, TypeVar, Union, Optional, List, Generic, Tuple
from abc import ABCMeta, abstractmethod


class ComparableType(metaclass=ABCMeta):

    @abstractmethod
    def __lt__(self, other: Any) -> bool: ...

    @abstractmethod
    def __le__(self, other: Any) -> bool: ...

    @abstractmethod
    def __gt__(self, other: Any) -> bool: ...

    @abstractmethod
    def __ge__(self, other: Any) -> bool: ...


CT = TypeVar('CT', bound=ComparableType)


class Node(metaclass=ABCMeta):

    @abstractmethod
    def insert_node(self, value: CT) -> Union[None, 'Node']: ...

    @abstractmethod
    def delete_node(self, value: CT) -> Union[None, 'Node']: ...


N = TypeVar('Node', bound=Node)
