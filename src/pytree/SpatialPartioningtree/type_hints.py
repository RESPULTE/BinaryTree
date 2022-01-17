from typing import Tuple, NewType, TypeVar, Any

UID = TypeVar("UID", bound=Any)

Num = TypeVar("Num", bound=float)

Point = NewType("Point", Tuple[Num, Num])

RGB = NewType("RGB", Tuple[int, int, int])
