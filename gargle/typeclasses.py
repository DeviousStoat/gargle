from __future__ import annotations

import typing as t

__all__ = (
    "Functor",
    "Applicative",
)

ValueT = t.TypeVar("ValueT")
OutT = t.TypeVar("OutT")


@t.runtime_checkable
class Functor(t.Protocol[ValueT]):
    def map(
        self: Functor[ValueT],
        func: t.Callable[[ValueT], OutT],
    ) -> Functor[OutT]:
        ...


@t.runtime_checkable
class Applicative(t.Protocol[ValueT]):
    def apply(
        self: Applicative[ValueT],
        func: Applicative[t.Callable[[ValueT], OutT]],
    ) -> Applicative[OutT]:
        ...


@t.runtime_checkable
class Monad(t.Protocol[ValueT]):
    def bind(
        self: Monad[ValueT],
        func: t.Callable[[ValueT], Monad[OutT]],
    ) -> Monad[OutT]:
        ...
