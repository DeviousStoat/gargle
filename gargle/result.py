from __future__ import annotations

import functools
import typing as t
from dataclasses import dataclass

from gargle import maybe

__all__ = ("Err", "Ok", "Result", "result_wrapped", "result_wrapped_for")
OutT = t.TypeVar("OutT")
OkT = t.TypeVar("OkT")
ErrT = t.TypeVar("ErrT")
ExcT = t.TypeVar("ExcT", bound=Exception)
P = t.ParamSpec("P")


class UnwrapError(Exception):
    ...


class _ResultInternal(t.Generic[OkT, ErrT]):
    def unwrap(self, exc: type[Exception] | None = None) -> OkT:
        """
        Unwrap the value in `Result`.
        Returning the value inside if `Ok else raising an exception.

        Exception used is `UnwrapError` unless other specified in `exc`.

        >>> Ok(5).unwrap()
        5

        >>> Err("bad value").unwrap()
        Traceback (most recent call last):
        ...
        gargle.result.UnwrapError: bad value
        """
        match t.cast(Result[OkT, ErrT], self):
            case Ok(value):
                return value
            case Err(err):
                if exc is not None:
                    raise exc(err)
                raise UnwrapError(err)

    def unwrap_or(self, default: OkT | t.Callable[[], OkT]) -> OkT:
        """
        Unwrap the value in `Result`.
        Returning the value inside if `Ok otherwise the `default`

        >>> Ok(5).unwrap_or(10)
        5

        >>> Err("bad value").unwrap_or(10)
        10
        """
        match t.cast(Result[OkT, ErrT], self):
            case Ok(value):
                return value
            case Err():
                return default() if callable(default) else default


@dataclass(frozen=True, repr=False)
class Ok(_ResultInternal[OkT, ErrT]):
    _value: OkT

    def __repr__(self) -> str:
        return f"Ok({self._value!r})"

    def __contains__(self, value: t.Any) -> bool:
        return self._value == value

    def unwrap_raise(self: Result[OkT, Exception]) -> OkT:
        """
        Like `unwrap` but `Err` value needs to be an exception and it will be raised

        >>> Ok(5).unwrap_raise()
        5

        >>> Err(ValueError("bad value")).unwrap_raise()
        Traceback (most recent call last):
        ...
        ValueError: bad value
        """
        return t.cast(Ok[OkT, ErrT], self)._value

    def map(self, func: t.Callable[[OkT], OutT]) -> Result[OutT, ErrT]:
        """
        Calls the `func` with the value wrapped in `Result` if `Ok`

        >>> Ok(5).map(lambda x: x + 1)
        Ok(6)

        >>> Err("bad value").map(lambda x: x + 1)
        Err('bad value')
        """
        return Ok(func(self._value))

    def map_or(
        self, func: t.Callable[[OkT], OutT], *, default: OutT | t.Callable[[], OutT]
    ) -> OutT:
        """
        Calls the `func` with the value wrapped in `Result` if `Ok`
        returning the unwrapped value else return `default`

        >>> Ok(5).map_or(lambda x: x + 1, default=10)
        6

        >>> Err("bad value").map_or(lambda x: x + 1, default=10)
        10

        >>> Err("bad value").map_or(lambda x: x + 1, default=lambda: int("10"))
        10
        """
        return func(self._value)

    def map_err(self, func: t.Callable[[ErrT], OutT]) -> Result[OkT, OutT]:
        """
        Like `map` but acts on the value in `Err`

        >>> Ok(5).map_err(lambda s: s.upper())
        Ok(5)

        >>> Err("bad value").map_err(lambda s: s.upper())
        Err('BAD VALUE')
        """
        return Ok(self._value)

    def and_(self, res: Result[OkT, ErrT]) -> Result[OkT, ErrT]:
        """
        Returns `Err` if the value is `Err` else returns `res`

        >>> Ok(5).and_(Err("bad value"))
        Err('bad value')

        >>> Ok(5).and_(Ok(6))
        Ok(6)

        >>> Err("bad value").and_(Ok(5))
        Err('bad value')
        """
        return res

    def and_then(
        self, func: t.Callable[[OkT], Result[OutT, ErrT]]
    ) -> Result[OutT, ErrT]:
        """
        Returns the result of calling `func` with the wrapped value if `Ok`
        else return the `Err`

        >>> Ok(5).and_then(lambda x: Ok(str(x + 10)))
        Ok('15')

        >>> Err("bad value").and_then(lambda x: Some(str(x + 10)))
        Err('bad value')
        """
        return func(self._value)

    def or_(
        self, res: Result[OkT, ErrT] | t.Callable[[], Result[OkT, ErrT]]
    ) -> Result[OkT, ErrT]:
        """
        Return value if `Ok` otherwise returns `res`

        >>> Ok(5).or_(Ok(6))
        Ok(5)

        >>> Err("bad value").or_(Ok(5))
        Ok(5)

        >>> Err("bad value").or_(lambda: Ok(str(10)))
        Ok('10')
        """
        return Ok(self._value)

    def ok(self) -> maybe.Maybe[OkT]:
        """
        Converts `Result` to `Maybe`, keeping `Ok` value

        >>> Ok(5).ok()
        Some(5)

        >>> Err("bad value").ok()
        Nothing()
        """
        return maybe.Some(self._value)

    def err(self) -> maybe.Maybe[ErrT]:
        """
        Converts `Result` to `Maybe`, keeping the `Err` value

        >>> Ok(5).err()
        Nothing()

        >>> Err("bad value").err()
        Some('bad value')
        """
        return maybe.Nothing()

    def either(
        self, ok_func: t.Callable[[OkT], OutT], err_func: t.Callable[[ErrT], OutT]
    ) -> OutT:
        """
        Either call `ok_func` with value if `Ok` else `err_func` with error value

        >>> Ok(5).either(lambda x: x + 1, lambda s: s.upper())
        6

        >>> Err("bad value").either(lambda x: x + 1, lambda s: s.upper())
        'BAD VALUE'
        """
        return ok_func(self._value)


@dataclass(frozen=True, repr=False)
class Err(_ResultInternal[OkT, ErrT]):
    _value: ErrT

    def __repr__(self) -> str:
        return f"Err({self._value!r})"

    def __contains__(self, value: t.Any) -> bool:
        return self._value == value

    def unwrap_raise(self: Result[OkT, Exception]) -> OkT:
        """
        Like `unwrap` but `Err` value needs to be an exception and it will be raised

        >>> Ok(5).unwrap_raise()
        5

        >>> Err(ValueError("bad value")).unwrap_raise()
        Traceback (most recent call last):
        ...
        ValueError: bad value
        """
        raise t.cast(Err[OkT, Exception], self)._value

    def map(self, func: t.Callable[[OkT], OutT]) -> Result[OutT, ErrT]:
        """
        Calls the `func` with the value wrapped in `Result` if `Ok`

        >>> Ok(5).map(lambda x: x + 1)
        Ok(6)

        >>> Err("bad value").map(lambda x: x + 1)
        Err('bad value')
        """
        return Err(self._value)

    def map_or(
        self, func: t.Callable[[OkT], OutT], *, default: OutT | t.Callable[[], OutT]
    ) -> OutT:
        """
        Calls the `func` with the value wrapped in `Result` if `Ok`
        returning the unwrapped value else return `default`

        >>> Ok(5).map_or(lambda x: x + 1, default=10)
        6

        >>> Err("bad value").map_or(lambda x: x + 1, default=10)
        10

        >>> Err("bad value").map_or(lambda x: x + 1, default=lambda: int("10"))
        10
        """
        return default() if callable(default) else default

    def map_err(self, func: t.Callable[[ErrT], OutT]) -> Result[OkT, OutT]:
        """
        Like `map` but acts on the value in `Err`

        >>> Ok(5).map_err(lambda s: s.upper())
        Ok(5)

        >>> Err("bad value").map_err(lambda s: s.upper())
        Err('BAD VALUE')
        """
        return Err(func(self._value))

    def and_(self, res: Result[OkT, ErrT]) -> Result[OkT, ErrT]:
        """
        Returns `Err` if the value is `Err` else returns `res`

        >>> Ok(5).and_(Err("bad value"))
        Err('bad value')

        >>> Ok(5).and_(Ok(6))
        Ok(6)

        >>> Err("bad value").and_(Ok(5))
        Err('bad value')
        """
        return Err(self._value)

    def and_then(
        self, func: t.Callable[[OkT], Result[OutT, ErrT]]
    ) -> Result[OutT, ErrT]:
        """
        Returns the result of calling `func` with the wrapped value if `Ok`
        else return the `Err`

        >>> Ok(5).and_then(lambda x: Ok(str(x + 10)))
        Ok('15')

        >>> Err("bad value").and_then(lambda x: Some(str(x + 10)))
        Err('bad value')
        """
        return Err(self._value)

    def or_(
        self, res: Result[OkT, ErrT] | t.Callable[[], Result[OkT, ErrT]]
    ) -> Result[OkT, ErrT]:
        """
        Return value if `Ok` otherwise returns `res`

        >>> Ok(5).or_(Ok(6))
        Ok(5)

        >>> Err("bad value").or_(Ok(5))
        Ok(5)

        >>> Err("bad value").or_(lambda: Ok(str(10)))
        Ok('10')
        """
        return res() if callable(res) else res

    def ok(self) -> maybe.Maybe[OkT]:
        """
        Converts `Result` to `Maybe`, keeping `Ok` value

        >>> Ok(5).ok()
        Some(5)

        >>> Err("bad value").ok()
        Nothing()
        """
        return maybe.Nothing()

    def err(self) -> maybe.Maybe[ErrT]:
        """
        Converts `Result` to `Maybe`, keeping the `Err` value

        >>> Ok(5).err()
        Nothing()

        >>> Err("bad value").err()
        Some('bad value')
        """
        return maybe.Some(self._value)

    def either(
        self, ok_func: t.Callable[[OkT], OutT], err_func: t.Callable[[ErrT], OutT]
    ) -> OutT:
        """
        Either call `ok_func` with value if `Ok` else `err_func` with error value

        >>> Ok(5).either(lambda x: x + 1, lambda s: s.upper())
        6

        >>> Err("bad value").either(lambda x: x + 1, lambda s: s.upper())
        'BAD VALUE'
        """
        return err_func(self._value)


Result = Ok[OkT, ErrT] | Err[OkT, ErrT]


def result_wrapped(func: t.Callable[P, OutT]) -> t.Callable[P, Result[OutT, Exception]]:
    """
    Decorator that wraps the result of the decorated function in `Result`.
    Catching any exception and storing it in `Err`

    >>> @result_wrapped
    ... def div(x: int, y: int) -> float:
    ...     return x / y

    >>> div(6, 3)
    Ok(2.0)

    >>> div(6, 0)
    Err(ZeroDivisionError('division by zero'))
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[OutT, Exception]:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as exc:
            return Err(exc)

    return wrapper


@t.overload
def result_wrapped_for(
    excs_to_catch: type[ExcT],
) -> t.Callable[[t.Callable[P, OutT]], t.Callable[P, Result[OutT, ExcT]]]:
    ...


@t.overload
def result_wrapped_for(
    excs_to_catch: tuple[type[Exception], ...]
) -> t.Callable[[t.Callable[P, OutT]], t.Callable[P, Result[OutT, Exception]]]:
    ...


def result_wrapped_for(
    excs_to_catch: type[Exception] | tuple[type[Exception], ...]
) -> t.Callable[[t.Callable[P, OutT]], t.Callable[P, Result[OutT, Exception]]]:
    """
    Like `result_wrapped` but you can specify an exception type or
    a tuple of exception types to catch.
    The others will be ignored and raised normally.

    >>> @result_wrapped_for(ZeroDivisionError)
    ... def div(x: int, y: int) -> float:
    ...     return x / y

    >>> div(6, 3)
    Ok(2.0)

    >>> div(6, 0)
    Err(ZeroDivisionError('division by zero'))

    >>> @result_wrapped_for((ValueError, TypeError))
    ... def div(x: int, y: int) -> float:
    ...     return x / y

    >>> div(6, 0)
    Traceback (most recent call last):
    ...
    ZeroDivisionError: division by zero
    """

    def decorator(func: t.Callable[P, OutT]) -> t.Callable[P, Result[OutT, Exception]]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[OutT, Exception]:
            try:
                return Ok(func(*args, **kwargs))
            except excs_to_catch as exc:
                return Err(exc)

        return wrapper

    return decorator
