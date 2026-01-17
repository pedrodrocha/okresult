from typing import Generic, TypeVar, Iterator
from .result import Result


"""
Type variable for a generic type A
"""
A = TypeVar("A", covariant=True)


"""
Type variable for a generic error type E
"""
E = TypeVar("E", covariant=True)


class Do(Generic[A, E]):
    __slots__ = ("_result",)


    def __init__(self, result: "Result[A, E]") -> None:
        self._result = result

    def __iter__(self) -> Iterator["Result[A, E]"]:
        yield self._result

        return self._result
    

def do(result: "Result[A, E]") -> "Do[A, E]":
    return Do(result)