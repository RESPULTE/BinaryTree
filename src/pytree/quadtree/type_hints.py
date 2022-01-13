from typing import Tuple, NewType, TypeVar

Num = TypeVar("Num", bound=float)
UID = TypeVar("UID", bound=int)
Point = NewType("Point", Tuple[Num, Num])
