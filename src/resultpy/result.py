from typing import TypeVar, Generic, Literal, Callable, cast
from abc import ABC, abstractmethod

"""
Type variable for a generic type A
"""
A = TypeVar("A")

"""
Type variable for a transformed generic type B
"""
B = TypeVar("B")

"""
Type variable for a generic error type E
"""
E = TypeVar("E")

"""
type variable for a transformed generic error type F
"""
F = TypeVar("F")


class Result(Generic[A, E], ABC):
    __slots__ = ("status", "value")
    status: Literal["ok", "err"]

    @staticmethod
    def ok(value: A) -> "Ok[A, E]":
        return Ok(value)

    @staticmethod
    def err(value: E) -> "Err[A, E]":
        return Err(value)

    def is_ok(self) -> bool:
        return self.status == "ok"

    def is_err(self) -> bool:
        return self.status == "err"

    @abstractmethod
    def map(self, fn: Callable[[A], B]) -> "Result[B, E]": ...

    @abstractmethod
    def mapErr(self, fn: Callable[[E], F]) -> "Result[A, F]": ...


class Ok(Result[A, E]):
    __slots__ = ("value",)
    __match_args__ = ("value",)

    status = "ok"

    def __init__(self, value: A) -> None:
        self.value: A = value

    def map(self, fn: Callable[[A], B]) -> "Ok[B, E]":
        """
        Transforms success value.

        Parameters
        ----------
        fn : Callable[[A], B]
            Transformation function.

        Returns
        -------
        Ok[B, E]
            Ok with transformed value.

        Examples
        --------
        >>> ok = Ok(2)
        >>> ok.map(lambda x: x * 2)
        Ok(4)
        """
        return Ok(fn(self.value))

    def mapErr(self, fn: Callable[[E], F]) -> "Ok[A, F]":
        """
        No-op for Ok. Returns self with new phantom error type.

        The error type E is not used at runtime in Ok, so this
        operation only changes the type signature without executing fn.

        Parameters
        ----------
        fn : Callable[[E], F]
            Transformation function (ignored, never called).

        Returns
        -------
        Ok[A, F]
            Self with updated phantom error type F.

        Examples
        --------
        >>> ok = Ok(2)
        >>> ok.mapErr(lambda e: str(e))  # Type changes E -> str
        Ok(2)

        Notes
        -----
        This is a type-level operation only. The function fn is never
        invoked because Ok does not contain an error value.
        """
        # SAFETY: E is phantom on Ok (not used at runtime).
        return cast("Ok[A, F]", self)

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Ok):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(("ok", self.value))


class Err(Result[A, E]):
    __slots__ = ("value",)
    __match_args__ = ("value",)

    status = "err"

    def __init__(self, value: E) -> None:
        self.value: E = value

    def __repr__(self) -> str:
        return f"Err({self.value!r})"

    def map(self, fn: Callable[[A], B]) -> "Err[B, E]":
        """
        No-op for Err. Returns self with new phantom success type.

        The success type A is not used at runtime in Err, so this
        operation only changes the type signature without executing fn.

        Parameters
        ----------
        fn : Callable[[A], B]
            Transformation function (ignored, never called).

        Returns
        -------
        Err[B, E]
            Self with updated phantom success type B.

        Examples
        --------
        >>> err = Err("error")
        >>> err.map(lambda x: x * 2)  # Type changes A -> int
        Err('error')

        Notes
        -----
        This is a type-level operation only. The function fn is never
        invoked because Err does not contain a success value.
        """
        # SAFETY: A is phantom on Err (not used at runtime).
        return cast("Err[B, E]", self)

    def mapErr(self, fn: Callable[[E], F]) -> "Err[A, F]":
        """
        Transforms error value.

        Parameters
        ----------
        fn : Callable[[E], F]
            Transformation function.

        Returns
        -------
        Err[A, F]
            Err with transformed error value.

        Examples
        --------
        >>> err = Err("error")
        >>> err.mapErr(lambda e: e.upper())
        Err("ERROR")
        """
        return Err(fn(self.value))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Err):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(("err", self.value))
