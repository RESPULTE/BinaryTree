from typing import Any, TypeVar, Union, Optional, List, Generic, Tuple, Protocol
from abc import ABCMeta, abstractmethod


class Comparable(metaclass=ABCMeta):

    @abstractmethod
    def __lt__(self, other: Any) -> bool: ...


    @abstractmethod
    def __le__(self, other: Any) -> bool: ...


    @abstractmethod
    def __gt__(self, other: Any) -> bool: ...


    @abstractmethod
    def __ge__(self, other: Any) -> bool: ...


CT = TypeVar('CT', bound=Comparable)


class Node(Protocol):

    def _insert(self, value: CT) -> None: ...

    def _delete(self, value: CT) -> None: ...

    

