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


class BinarySearchNode(metaclass=ABCMeta):

    @abstractmethod
    def insert(self, value: CT) -> 'BinarySearchNode': ...

    @abstractmethod
    def delete(self, value: CT) -> 'BinarySearchNode': ...


Node = TypeVar('Node', bound=BinarySearchNode)
