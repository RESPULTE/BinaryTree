from typing import Tuple, NewType, TypeVar, Any

Num = TypeVar("Num", bound=float)
Point = NewType("Point", Tuple[Num, Num])

UID = TypeVar("UID", bound=Any)
