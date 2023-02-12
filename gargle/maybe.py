from __future__ import annotations

import typing as t
from dataclasses import dataclass

from gargle import result

__all__ = (
    "Maybe",
    "Nothing",
    "Some",
    "as_maybe",
    "from_maybe",
    "is_nothing",
    "is_some",
    "is_maybe",
    "sequence",
)
ValueT = t.TypeVar("ValueT", contravariant=True)
OutT = t.TypeVar("OutT")
T = t.TypeVar("T")
T2 = t.TypeVar("T2")
T3 = t.TypeVar("T3")
T4 = t.TypeVar("T4")
T5 = t.TypeVar("T5")


class _MaybeInternal(t.Generic[ValueT]):
    """
    Internal class gathering common methods for the maybe classes.
    """

    @t.overload
    def from_maybe(self, *, default: t.Callable[[], T] | T) -> ValueT | T:
        ...

    @t.overload
    def from_maybe(self, *, default: T | None = None) -> ValueT | T | None:
        ...

    def from_maybe(
        self, *, default: t.Callable[[], T] | T | None = None
    ) -> ValueT | T | None:
        """
        Unwraps the value in the `Maybe`
        `Nothing` returns `None` unless `default` is specified

        >>> Some(5).from_maybe()
        5

        >>> Some(5).from_maybe(default=10)
        5

        >>> Nothing().from_maybe() is None
        True

        >>> Nothing().from_maybe(default=10)
        10

        >>> Nothing().from_maybe(default=lambda: int("10"))
        10
        """
        return from_maybe(t.cast(Maybe[ValueT], self), default=default)

    def is_nothing(self) -> bool:
        """
        Checks if a maybe value is `Nothing`

        >>> is_nothing(Some(5))
        False

        >>> is_nothing(Nothing())
        True
        """
        return isinstance(self, Nothing)

    def is_some(self) -> bool:
        """
        Checks if a maybe value is `Some`

        >>> is_some(Some(5))
        True

        >>> is_some(Nothing())
        False
        """
        return isinstance(self, Some)


@dataclass(frozen=True, repr=False)
class Some(_MaybeInternal[ValueT]):
    _value: ValueT

    def __repr__(self) -> str:
        return f"Some({self._value!r})"

    def __contains__(self, value: t.Any) -> bool:
        return self._value == value

    def map(self, func: t.Callable[[ValueT], OutT]) -> Maybe[OutT]:
        """
        Calls the `func` with the value wrapped in `Maybe` if `Some`

        >>> Some(5).map(lambda x: x + 1)
        Some(6)

        >>> Nothing().map(lambda x: x + 1)
        Nothing()
        """
        return Some(func(self._value))

    def map_or(
        self, func: t.Callable[[ValueT], OutT], *, default: OutT | t.Callable[[], OutT]
    ) -> OutT:
        """
        Calls the `func` with the value wrapped in `Maybe` if `Some`
        returning the unwrapped value else return `default`

        >>> Some(5).map_or(lambda x: x + 1, default=10)
        6

        >>> Nothing().map_or(lambda x: x + 1, default=10)
        10

        >>> Nothing().map_or(lambda x: x + 1, default=lambda: int("10"))
        10
        """
        return func(self._value)

    def and_(self, mayb: Maybe[T]) -> Maybe[T]:
        """
        Returns `Nothing` if the value is `Nothing` else returns `mayb`

        >>> Some(5).and_(Nothing())
        Nothing()

        >>> Some(5).and_(Some(6))
        Some(6)

        >>> Nothing().and_(Some(5))
        Nothing()
        """
        return mayb

    def and_then(self, func: t.Callable[[ValueT], Maybe[OutT]]) -> Maybe[OutT]:
        """
        Returns the result of calling `func` with the wrapped value if `Some`
        else `Nothing`

        >>> Some(5).and_then(lambda x: Some(str(x + 10)))
        Some('15')

        >>> Nothing().and_then(lambda x: Some(str(x + 10)))
        Nothing()
        """
        return func(self._value)

    def and_then_opt(self, func: t.Callable[[ValueT], OutT | None]) -> Maybe[OutT]:
        """
        Same as `and_then` but `func` returns `value | None` which gets wrapped
        to `Maybe` through `as_maybe`

        >>> Some("key1").and_then_opt(lambda k: {"key1": "value1"}.get(k))
        Some('value1')

        >>> Some("key2").and_then_opt(lambda k: {"key1": "value1"}.get(k))
        Nothing()

        >>> Nothing().and_then_opt(lambda k: {"key1": "value1"}.get(k))
        Nothing()
        """
        return as_maybe(func(self._value))

    @t.overload
    def get(self: Maybe[dict[T, T2]], key: T) -> Maybe[T2]:
        ...

    @t.overload
    def get(self: Maybe[list[T]], key: int) -> Maybe[T]:
        ...

    def get(self: Maybe[t.Any], key: t.Any) -> Maybe[T] | Maybe[T2]:
        """
        Tries to get the values assigned to `key` in the wrapped sequence

        >>> Some([1, 2, 3]).get(1)
        Some(2)

        >>> Some([1, 2, 3]).get(5)
        Nothing()

        >>> Some({"key1": "value1"}).get("key1")
        Some('value1')

        >>> Some({"key1": "value1"}).get("key2")
        Nothing()

        >>> Nothing().get(2)
        Nothing()
        """
        try:
            return self.map(lambda v: v[key])
        except (IndexError, KeyError, TypeError):
            return Nothing()

    def filter(self, predicate: t.Callable[[ValueT], bool]) -> Maybe[ValueT]:
        """
        Checks if `Some` and the wrapped value passes the `predicate`

        >>> Some(5).filter(lambda x: x > 2)
        Some(5)

        >>> Some(5).filter(lambda x: x > 10)
        Nothing()

        >>> Nothing().filter(lambda x: x > 2)
        Nothing()
        """
        return Some(self._value) if predicate(self._value) else Nothing()

    def or_(self, mayb: Maybe[ValueT] | t.Callable[[], Maybe[ValueT]]) -> Maybe[ValueT]:
        """
        Return value if `Some` otherwise returns `mayb`

        >>> Some(5).or_(Some(6))
        Some(5)

        >>> Nothing().or_(Some(5))
        Some(5)

        >>> Nothing().or_(lambda: Some(str(10)))
        Some('10')
        """
        return Some(self._value)

    def xor(self, mayb: Maybe[ValueT]) -> Maybe[ValueT]:
        """
        Checks if exactly one of the `Maybe`s are `Some`

        >>> Some(5).xor(Some(6))
        Nothing()

        >>> Some(5).xor(Nothing())
        Some(5)

        >>> Nothing().xor(Some(5))
        Some(5)

        >>> Nothing().xor(Nothing())
        Nothing()
        """
        match mayb:
            case Nothing():
                return Some(self._value)
            case _:
                return Nothing()

    @t.overload
    def zip(self, mayb1: Maybe[T], /) -> Maybe[tuple[ValueT, T]]:
        ...

    @t.overload
    def zip(self, mayb1: Maybe[T], mayb2: Maybe[T2], /) -> Maybe[tuple[ValueT, T, T2]]:
        ...

    @t.overload
    def zip(
        self, mayb1: Maybe[T], mayb2: Maybe[T2], mayb3: Maybe[T3], /
    ) -> Maybe[tuple[ValueT, T, T2, T3]]:
        ...

    @t.overload
    def zip(
        self, mayb1: Maybe[T], mayb2: Maybe[T2], mayb3: Maybe[T3], mayb4: Maybe[T4], /
    ) -> Maybe[tuple[ValueT, T, T2, T3, T4]]:
        ...

    @t.overload
    def zip(
        self,
        mayb1: Maybe[T],
        mayb2: Maybe[T2],
        mayb3: Maybe[T3],
        mayb4: Maybe[T4],
        mayb5: Maybe[T5],
        /,
    ) -> Maybe[tuple[ValueT, T, T2, T3, T4, T5]]:
        ...

    def zip(self, *maybs: Maybe[t.Any]) -> Maybe[tuple[t.Any, ...]]:
        """
        Zips the `Maybe` with several other `Maybe`s if they are all `Some`

        >>> Some(5).zip(Some(6))
        Some((5, 6))

        >>> Some(5).zip(Some(6), Some(7))
        Some((5, 6, 7))

        >>> Some(5).zip(Nothing())
        Nothing()

        >>> Nothing().zip(Some(6))
        Nothing()
        """
        match sequence(maybs):
            case Some(values):
                return Some((self._value, *values))
            case Nothing():
                return Nothing()

    @t.overload
    def zip_with(
        self, func: t.Callable[[ValueT, T], OutT], mayb1: Maybe[T], /
    ) -> Maybe[OutT]:
        ...

    @t.overload
    def zip_with(
        self,
        func: t.Callable[[ValueT, T, T2], OutT],
        mayb1: Maybe[T],
        mayb2: Maybe[T2],
        /,
    ) -> Maybe[OutT]:
        ...

    @t.overload
    def zip_with(
        self,
        func: t.Callable[[ValueT, T, T2, T3], OutT],
        mayb1: Maybe[T],
        mayb2: Maybe[T2],
        mayb3: Maybe[T3],
        /,
    ) -> Maybe[OutT]:
        ...

    @t.overload
    def zip_with(
        self,
        func: t.Callable[[ValueT, T, T2, T3, T4], OutT],
        mayb1: Maybe[T],
        mayb2: Maybe[T2],
        mayb3: Maybe[T3],
        mayb4: Maybe[T4],
        /,
    ) -> Maybe[OutT]:
        ...

    @t.overload
    def zip_with(
        self,
        func: t.Callable[[ValueT, T, T2, T3, T4, T5], OutT],
        mayb1: Maybe[T],
        mayb2: Maybe[T2],
        mayb3: Maybe[T3],
        mayb4: Maybe[T4],
        mayb5: Maybe[T5],
        /,
    ) -> Maybe[OutT]:
        ...

    def zip_with(
        self, func: t.Callable[..., OutT], *maybs: Maybe[t.Any]
    ) -> Maybe[OutT]:
        """
        Like `zip` but passes all the unwrapped values in `func` instead of
        building a tuple with them

        >>> def merge_dicts(d1: dict, d2: dict) -> dict:
        ...     return d1 | d2

        >>> Some({"key1": "value1"}).zip_with(merge_dicts, Some({"key2": "value2"}))
        Some({'key1': 'value1', 'key2': 'value2'})

        >>> Nothing().zip_with(merge_dicts, Some({"key2": "value2"}))
        Nothing()
        """
        return self.zip(*maybs).map(lambda values: func(*values))

    def unzip(self: Maybe[tuple[T, T2]]) -> tuple[Maybe[T], Maybe[T2]]:
        """
        Turns a `Maybe tuple` into a `tuple` of `Maybe`s

        >>> Some((1, 2)).unzip()
        (Some(1), Some(2))

        >>> Nothing().unzip()
        (Nothing(), Nothing())
        """
        return tuple(
            (Some(value) for value in t.cast(Some[tuple[t.Any, ...]], self)._value)
        )

    def ok_or(self, err: T | t.Callable[[], T]) -> result.Result[ValueT, T]:
        """
        Convert `Maybe` to `Result`

        >>> Some(5).ok_or("bad value")
        Ok(5)

        >>> Nothing().ok_or("bad value")
        Err('bad value')
        """
        return result.Ok(self._value)


@dataclass(frozen=True, repr=False)
class Nothing(_MaybeInternal[ValueT]):
    def __contains__(self, value: t.Any) -> bool:
        return False

    def __repr__(self) -> str:
        return "Nothing()"

    def map(self, func: t.Callable[[ValueT], OutT]) -> Maybe[OutT]:
        """
        Calls the `func` with the value wrapped in `Maybe` if `Some`

        >>> Some(5).map(lambda x: x + 1)
        Some(6)

        >>> Nothing().map(lambda x: x + 1)
        Nothing()
        """
        return Nothing()

    def map_or(
        self, func: t.Callable[[ValueT], OutT], *, default: OutT | t.Callable[[], OutT]
    ) -> OutT:
        """
        Calls the `func` with the value wrapped in `Maybe` if `Some`
        returning the unwrapped value else return `default`

        >>> Some(5).map_or(lambda x: x + 1, default=10)
        6

        >>> Nothing().map_or(lambda x: x + 1, default=10)
        10

        >>> Nothing().map_or(lambda x: x + 1, default=lambda: int("10"))
        10
        """
        return default() if callable(default) else default

    def and_(self, mayb: Maybe[T]) -> Maybe[T]:
        """
        Returns `Nothing` if the value is `Nothing` else returns `mayb`

        >>> Some(5).and_(Nothing())
        Nothing()

        >>> Some(5).and_(Some(6))
        Some(6)

        >>> Nothing().and_(Some(5))
        Nothing()
        """
        return Nothing()

    def and_then(self, func: t.Callable[[ValueT], Maybe[OutT]]) -> Maybe[OutT]:
        """
        Returns the result of calling `func` with the wrapped value if `Some`
        else `Nothing`

        >>> Some(5).and_then(lambda x: Some(str(x + 10)))
        Some('15')

        >>> Nothing().and_then(lambda x: Some(str(x + 10)))
        Nothing()
        """
        return Nothing()

    def and_then_opt(self, func: t.Callable[[ValueT], OutT | None]) -> Maybe[OutT]:
        """
        Same as `and_then` but `func` returns `value | None` which gets wrapped
        to `Maybe` through `as_maybe`

        >>> Some("key1").and_then_opt(lambda k: {"key1": "value1"}.get(k))
        Some('value1')

        >>> Some("key2").and_then_opt(lambda k: {"key1": "value1"}.get(k))
        Nothing()

        >>> Nothing().and_then_opt(lambda k: {"key1": "value1"}.get(k))
        Nothing()
        """
        return Nothing()

    @t.overload
    def get(self: Maybe[dict[T, T2]], key: T) -> Maybe[T2]:
        ...

    @t.overload
    def get(self: Maybe[list[T]], key: int) -> Maybe[T]:
        ...

    def get(self: Maybe[t.Any], key: t.Any) -> Maybe[T] | Maybe[T2]:
        """
        Tries to get the values assigned to `key` in the wrapped sequence

        >>> Some([1, 2, 3]).get(1)
        Some(2)

        >>> Some([1, 2, 3]).get(5)
        Nothing()

        >>> Some({"key1": "value1"}).get("key1")
        Some('value1')

        >>> Some({"key1": "value1"}).get("key2")
        Nothing()

        >>> Nothing().get(2)
        Nothing()
        """
        return Nothing()

    def filter(self, predicate: t.Callable[[ValueT], bool]) -> Maybe[ValueT]:
        """
        Checks if `Some` and the wrapped value passes the `predicate`

        >>> Some(5).filter(lambda x: x > 2)
        Some(5)

        >>> Some(5).filter(lambda x: x > 10)
        Nothing()

        >>> Nothing().filter(lambda x: x > 2)
        Nothing()
        """
        return Nothing()

    def or_(self, mayb: Maybe[ValueT] | t.Callable[[], Maybe[ValueT]]) -> Maybe[ValueT]:
        """
        Return value if `Some` otherwise returns `mayb`

        >>> Some(5).or_(Some(6))
        Some(5)

        >>> Nothing().or_(Some(5))
        Some(5)

        >>> Nothing().or_(lambda: Some(str(10)))
        Some('10')
        """
        return mayb() if callable(mayb) else mayb

    def xor(self, mayb: Maybe[ValueT]) -> Maybe[ValueT]:
        """
        Checks if exactly one of the `Maybe`s are `Some`

        >>> Some(5).xor(Some(6))
        Nothing()

        >>> Some(5).xor(Nothing())
        Some(5)

        >>> Nothing().xor(Some(5))
        Some(5)

        >>> Nothing().xor(Nothing())
        Nothing()
        """
        match mayb:
            case Some(value):
                return Some(value)
            case _:
                return Nothing()

    @t.overload
    def zip(self, mayb1: Maybe[T], /) -> Maybe[tuple[ValueT, T]]:
        ...

    @t.overload
    def zip(self, mayb1: Maybe[T], mayb2: Maybe[T2], /) -> Maybe[tuple[ValueT, T, T2]]:
        ...

    @t.overload
    def zip(
        self, mayb1: Maybe[T], mayb2: Maybe[T2], mayb3: Maybe[T3], /
    ) -> Maybe[tuple[ValueT, T, T2, T3]]:
        ...

    @t.overload
    def zip(
        self, mayb1: Maybe[T], mayb2: Maybe[T2], mayb3: Maybe[T3], mayb4: Maybe[T4], /
    ) -> Maybe[tuple[ValueT, T, T2, T3, T4]]:
        ...

    @t.overload
    def zip(
        self,
        mayb1: Maybe[T],
        mayb2: Maybe[T2],
        mayb3: Maybe[T3],
        mayb4: Maybe[T4],
        mayb5: Maybe[T5],
        /,
    ) -> Maybe[tuple[ValueT, T, T2, T3, T4, T5]]:
        ...

    def zip(self, *maybs: Maybe[t.Any]) -> Maybe[tuple[t.Any, ...]]:
        """
        Zips the `Maybe` with several other `Maybe`s if they are all `Some`

        >>> Some(5).zip(Some(6))
        Some((5, 6))

        >>> Some(5).zip(Some(6), Some(7))
        Some((5, 6, 7))

        >>> Some(5).zip(Nothing())
        Nothing()

        >>> Nothing().zip(Some(6))
        Nothing()
        """
        return Nothing()

    @t.overload
    def zip_with(
        self, func: t.Callable[[ValueT, T], OutT], mayb1: Maybe[T], /
    ) -> Maybe[OutT]:
        ...

    @t.overload
    def zip_with(
        self,
        func: t.Callable[[ValueT, T, T2], OutT],
        mayb1: Maybe[T],
        mayb2: Maybe[T2],
        /,
    ) -> Maybe[OutT]:
        ...

    @t.overload
    def zip_with(
        self,
        func: t.Callable[[ValueT, T, T2, T3], OutT],
        mayb1: Maybe[T],
        mayb2: Maybe[T2],
        mayb3: Maybe[T3],
        /,
    ) -> Maybe[OutT]:
        ...

    @t.overload
    def zip_with(
        self,
        func: t.Callable[[ValueT, T, T2, T3, T4], OutT],
        mayb1: Maybe[T],
        mayb2: Maybe[T2],
        mayb3: Maybe[T3],
        mayb4: Maybe[T4],
        /,
    ) -> Maybe[OutT]:
        ...

    @t.overload
    def zip_with(
        self,
        func: t.Callable[[ValueT, T, T2, T3, T4, T5], OutT],
        mayb1: Maybe[T],
        mayb2: Maybe[T2],
        mayb3: Maybe[T3],
        mayb4: Maybe[T4],
        mayb5: Maybe[T5],
        /,
    ) -> Maybe[OutT]:
        ...

    def zip_with(
        self, func: t.Callable[..., OutT], *maybs: Maybe[t.Any]
    ) -> Maybe[OutT]:
        """
        Like `zip` but passes all the unwrapped values in `func` instead of
        building a tuple with them

        >>> def merge_dicts(d1: dict, d2: dict) -> dict:
        ...     return d1 | d2

        >>> Some({"key1": "value1"}).zip_with(merge_dicts, Some({"key2": "value2"}))
        Some({'key1': 'value1', 'key2': 'value2'})

        >>> Nothing().zip_with(merge_dicts, Some({"key2": "value2"}))
        Nothing()
        """
        return Nothing()

    def unzip(self: Maybe[tuple[T, T2]]) -> tuple[Maybe[T], Maybe[T2]]:
        """
        Turns a `Maybe tuple` into a `tuple` of `Maybe`s

        >>> Some((1, 2)).unzip()
        (Some(1), Some(2))

        >>> Nothing().unzip()
        (Nothing(), Nothing())
        """
        return (Nothing(), Nothing())

    def ok_or(self, err: T | t.Callable[[], T]) -> result.Result[ValueT, T]:
        """
        Convert `Maybe` to `Result`

        >>> Some(5).ok_or("bad value")
        Ok(5)

        >>> Nothing().ok_or("bad value")
        Err('bad value')
        """
        return result.Err(err()) if callable(err) else result.Err(err)


Maybe = Some[ValueT] | Nothing[ValueT]


@t.overload
def from_maybe(
    maybe_value: Maybe[ValueT], *, default: t.Callable[[], T] | T
) -> ValueT | T:
    ...


@t.overload
def from_maybe(
    maybe_value: Maybe[ValueT], *, default: T | None = None
) -> ValueT | T | None:
    ...


def from_maybe(
    maybe_value: Maybe[ValueT], *, default: t.Callable[[], T] | T | None = None
) -> ValueT | T | None:
    """
    Unwraps the value in a `Maybe`
    `Nothing` returns `None` unless `default` is specified

    >>> from_maybe(Some(5))
    5

    >>> from_maybe(Some(5), default=10)
    5

    >>> from_maybe(Nothing()) is None
    True

    >>> from_maybe(Nothing(), default=10)
    10

    >>> from_maybe(Nothing(), default=lambda: int("10"))
    10
    """
    match maybe_value:
        case Some(value):
            return value
        case Nothing() if default is None:
            return None
        case Nothing():
            if callable(default):
                return default()
            return default


def as_maybe(value: ValueT | None) -> Maybe[ValueT]:
    """
    Wraps a value in `Maybe`

    >>> as_maybe(5)
    Some(5)

    >>> as_maybe(None)
    Nothing()
    """
    if value is None:
        return Nothing()
    return Some(value)


def is_nothing(maybe_value: Maybe[ValueT]) -> t.TypeGuard[Nothing[ValueT]]:
    """
    Checks if a maybe value is `Nothing`

    >>> is_nothing(Some(5))
    False

    >>> is_nothing(Nothing())
    True
    """
    return maybe_value.is_nothing()


def is_some(maybe_value: Maybe[ValueT]) -> t.TypeGuard[Some[ValueT]]:
    """
    Checks if a maybe value is `Some`

    >>> is_some(Some(5))
    True

    >>> is_some(Nothing())
    False
    """
    return maybe_value.is_some()


def is_maybe(value: t.Any) -> t.TypeGuard[Maybe[t.Any]]:
    """
    Checks if a value is `Maybe`, either `Some` or `Nothing`

    >>> is_maybe(Some(5))
    True

    >>> is_maybe(Nothing())
    True

    >>> is_maybe(5)
    False
    """
    return isinstance(value, (Some, Nothing))


@t.overload
def maybe_get(some_seq: t.Sequence[T], key: int) -> Maybe[T]:
    ...


@t.overload
def maybe_get(some_seq: t.Mapping[T, T2], key: T) -> Maybe[T2]:
    ...


def maybe_get(some_seq: t.Any, key: t.Any) -> Maybe[T] | Maybe[T2]:
    """
    Tries to get a value from the sequence returning a `Maybe`
    `Nothing` if the value doesn't exist in the sequence
    otherwise the value wrapped in `Some`

    >>> maybe_get([1, 2, 3], 1)
    Some(2)

    >>> maybe_get([1, 2, 3], 5)
    Nothing()

    >>> maybe_get({"key1": "value1"}, "key1")
    Some('value1')

    >>> maybe_get({"key1": "value1"}, "key2")
    Nothing()
    """
    try:
        return Some(some_seq[key])
    except (KeyError, IndexError):
        return Nothing()


def sequence(mayb_iter: t.Iterable[Maybe[T]]) -> Maybe[list[T]]:
    """
    Turns an iterable of `Maybe`s into a `Maybe` list

    >>> sequence([Some(1), Some(2), Some(3)])
    Some([1, 2, 3])

    >>> sequence([Some(1), Some(2), Nothing()])
    Nothing()

    >>> sequence((Some(1), Some(2), Some(3)))
    Some([1, 2, 3])

    >>> sequence((Some(1), Some(2), Nothing()))
    Nothing()
    """
    res: list[T] = []
    for mayb in mayb_iter:
        match mayb:
            case Some(value):
                res.append(value)
            case Nothing():
                return Nothing()
    return Some(res)
