"""
Generic utilities for predicate functions; functions in the form of `a -> bool`
"""
from datetime import date
from typing import Any, Callable, Generic, Optional, TypeVar, cast

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


def identity(a: A) -> A:
    return a


class Predicate(Generic[A]):
    def __init__(self, p: Callable[[A], bool]) -> None:
        self.p = p

    def __call__(self, a: A) -> bool:
        return self.p(a)

    def __and__(self, other: 'Predicate[A]') -> 'Predicate[A]':
        return and_(self, other)

    def __invert__(self) -> 'Predicate[A]':
        return not_(self)

    def contramap(self, f: Callable[[B], A]) -> 'Predicate[B]':
        """Convert this P[A] into a P[B] by giving a method to convert Bs to As"""
        def p(b: B) -> bool:
            a: A = f(b)
            return self.p(a)
        return Predicate(p)

    def contramap_opt(self, f: Callable[[B], Optional[A]]) -> 'Predicate[B]':
        def p(b: B) -> bool:
            a: Optional[A] = f(b)
            return a is not None and self.p(a)
        return Predicate(p)

    def cast_callable(self) -> Callable[[A], bool]:
        """Work around https://github.com/python/mypy/issues/797 by casting."""
        return cast(Callable[[A], bool], self)


true: Predicate[Any] = Predicate(lambda a: True)
false: Predicate[Any] = Predicate(lambda a: False)


def not_(p: Predicate[A]) -> Predicate[A]:
    return Predicate(lambda a: not p(a))


def and_(p1: Predicate[A], p2: Predicate[A]) -> Predicate[A]:
    # The extra checks are just to avoid excess nesting of lambdas
    if p1 is true:
        return p2
    if p2 is true:
        return p1
    if p1 is false or p2 is false:
        return false
    return Predicate(lambda a: p1(a) and p2(a))


def compose(f: Callable[[A], B], g: Callable[[B], C]) -> Callable[[A], C]:
    return lambda a: g(f(a))


def date_in_range(start: date=None, end: date=None) -> Predicate[date]:
    """
    Returns a predicate for an inclusive date range.
    Predicate returns true iff `start <= date < end`
    """
    if start is None and end is None:
        raise ValueError("Need to at least one of start or end")
    startp: Predicate[date] = Predicate(lambda d: d >= start if start is not None else true)  # type: ignore
    endp: Predicate[date] = Predicate(lambda d: d < end if end is not None else true)  # type: ignore
    pred = startp & endp
    return pred
