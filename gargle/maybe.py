from __future__ import annotations
from dataclasses import dataclass
import typing as t

from gargle.typeclasses import OutT, ValueT


__all__ = (
    "Maybe",
    "Nothing",
    "Some",
    "from_maybe",
    "as_maybe",
)


class _MaybeInternal(t.Generic[ValueT]):
    """
    Internal class gathering common methods for the maybe classes.
    """

    def from_maybe(self, default: ValueT | None = None) -> ValueT | None:
        return from_maybe(t.cast(Maybe[ValueT], self), default)


@dataclass(frozen=True)
class Some(_MaybeInternal[ValueT]):
    _value: ValueT

    @property
    def value(self) -> ValueT:
        return self._value

    def map(self, func: t.Callable[[ValueT], OutT]) -> Some[OutT]:
        return Some(func(self.value))


@dataclass(frozen=True)
class Nothing(_MaybeInternal[None]):
    def map(self, _: t.Callable[[t.Any], t.Any]) -> Nothing:
        return Nothing()


Maybe = Some[ValueT] | Nothing


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
