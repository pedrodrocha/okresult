from typing import TypeVar, Union, Generic, TypeAlias

"""
Type variable for a generic type A
"""
A = TypeVar("A")

"""
Type variable for a transformed generic type B
"""
B = TypeVar("B")

"""
Type variable for a generic type E
"""
E = TypeVar("E")


class Ok(Generic[A]):
    __slots__ = ("value",)
    __match_args__ = ("value",)

    status: str = "ok"

    def __init__(self, value: A) -> None:
        self.value: A = value

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


class Err(Generic[E]):
    __slots__ = ("value",)
    __match_args__ = ("value",)

    status: str = "err"

    def __init__(self, value: E) -> None:
        self.value: E = value

    def __repr__(self) -> str:
        return f"Err({self.value!r})"


class Result:

    @staticmethod
    def ok(value: A) -> Ok[A]:
        return Ok(value)

    @staticmethod
    def err(value: E) -> Err[E]:
        return Err(value)


Res: TypeAlias = Union[Ok[A], Err[E]]
