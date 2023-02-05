from __future__ import annotations
from dataclasses import dataclass
import typing as t

from gargle.typeclasses import OutT, ValueT


__all__ = (
    "Maybe",
    "Nothing",
    "Some",
    "as_maybe",
    "from_maybe",
    "is_nothing",
    "is_some",
)


T = t.TypeVar("T")
T2 = t.TypeVar("T2")


class _MaybeInternal(t.Generic[ValueT]):
    """
    Internal class gathering common methods for the maybe classes.
    """

    @t.overload
    def from_maybe(self, default: ValueT) -> ValueT:
        ...

    @t.overload
    def from_maybe(self, default: ValueT | None = None) -> ValueT | None:
        ...

    def from_maybe(self, default: ValueT | None = None) -> ValueT | None:
        return from_maybe(t.cast(Maybe[ValueT], self), default)

    def is_nothing(self) -> bool:
        return isinstance(self, Nothing)

    def is_some(self) -> bool:
        return isinstance(self, Some)


@dataclass(frozen=True)
class Some(_MaybeInternal[ValueT]):
    _value: ValueT

    @property
    def value(self) -> ValueT:
        return self._value

    def map(self, func: t.Callable[[ValueT], OutT]) -> Maybe[OutT]:
        return Some(func(self.value))

    def apply(self, func: Maybe[t.Callable[[ValueT], OutT]]) -> Maybe[OutT]:
        match func:
            case Some(f):
                return self.map(f)
            case Nothing():
                return Nothing()

    def bind(self, func: t.Callable[[ValueT], Maybe[OutT]]) -> Maybe[OutT]:
        return func(self.value)

    def bind_opt(self, func: t.Callable[[ValueT], OutT | None]) -> Maybe[OutT]:
        return as_maybe(func(self.value))

    @t.overload
    def get(self: Maybe[list[T]], key: int) -> Maybe[T]:
        ...

    @t.overload
    def get(self: Maybe[dict[T, T2]], key: T) -> Maybe[T2]:
        ...

    def get(self: Maybe[t.Any], key: t.Any) -> Maybe[T] | Maybe[T2]:
        try:
            return self.map(lambda v: v[key])
        except (IndexError, KeyError):
            return Nothing()


@dataclass(frozen=True)
class Nothing(_MaybeInternal[ValueT]):
    def map(self, _: t.Callable[[ValueT], OutT]) -> Maybe[OutT]:
        return Nothing()

    def apply(self, _: Maybe[t.Callable[[ValueT], OutT]]) -> Maybe[OutT]:
        return Nothing()

    def bind(self, _: t.Callable[[ValueT], Maybe[OutT]]) -> Maybe[OutT]:
        return Nothing()

    def bind_opt(self, _: t.Callable[[ValueT], OutT | None]) -> Maybe[OutT]:
        return Nothing()

    @t.overload
    def get(self: Maybe[list[T]], key: int) -> Maybe[T]:
        ...

    @t.overload
    def get(self: Maybe[dict[T, T2]], key: T) -> Maybe[T2]:
        ...

    def get(self: Maybe[t.Any], key: t.Any) -> Maybe[T] | Maybe[T2]:
        return Nothing()


Maybe = Some[ValueT] | Nothing[ValueT]


@t.overload
def from_maybe(
    maybe_value: Maybe[ValueT],
    default: ValueT,
) -> ValueT:
    ...


@t.overload
def from_maybe(
    maybe_value: Maybe[ValueT],
    default: ValueT | None = None,
) -> ValueT | None:
    ...


def from_maybe(
    maybe_value: Maybe[ValueT],
    default: ValueT | None = None,
) -> ValueT | None:
    match maybe_value:
        case Some(value):
            return value
        case Nothing() if default is None:
            return None
        case Nothing():
            return default


def as_maybe(value: ValueT | None) -> Maybe[ValueT]:
    if value is None:
        return Nothing()

    return Some(value)


def is_nothing(maybe_value: Maybe[ValueT]) -> t.TypeGuard[Nothing[ValueT]]:
    return maybe_value.is_nothing()


def is_some(maybe_value: Maybe[ValueT]) -> t.TypeGuard[Some[ValueT]]:
    return maybe_value.is_some()


@t.overload
def maybe_get(some_seq: dict[T, T2], key: T) -> Maybe[T2]:
    ...


@t.overload
def maybe_get(some_seq: list[T], key: int) -> Maybe[T]:
    ...


def maybe_get(some_seq: t.Any, key: t.Any) -> Maybe[T] | Maybe[T2]:
    try:
        return Some(some_seq[key])
    except (KeyError, IndexError):
        return Nothing()
