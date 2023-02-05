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
)


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


@dataclass(frozen=True)
class Nothing(_MaybeInternal[ValueT]):
    def map(self, _: t.Callable[[ValueT], t.Any]) -> Maybe[ValueT]:
        return Nothing()

    def apply(self, _: Maybe[t.Callable[[ValueT], t.Any]]) -> Maybe[ValueT]:
        return Nothing()

    def bind(self, _: t.Callable[[ValueT], Maybe[t.Any]]) -> Maybe[ValueT]:
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
