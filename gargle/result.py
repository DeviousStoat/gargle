from __future__ import annotations

import functools
import typing as t
from dataclasses import dataclass

from gargle.typeclasses import OutT

__all__ = (
    "Err",
    "Ok",
    "Result",
    "either",
    "safe",
)

OkT = t.TypeVar("OkT")
ErrT = t.TypeVar("ErrT")

P = t.ParamSpec("P")


class _ResultInternal(t.Generic[OkT, ErrT]):
    def unwrap(self, exc: type[Exception] | None = None) -> OkT:
        """
        Unwrap the value in `Result`.
        Returning the value inside if `Ok else raising an exception.

        Exception used is `RuntimeError` unless other specified in `exc`.
        """
        match t.cast(Result[OkT, ErrT], self):
            case Ok(value):
                return value
            case Err(err):
                if exc is not None:
                    raise exc(err)

                raise RuntimeError(err)


@dataclass
class Ok(_ResultInternal[OkT, ErrT]):
    _value: OkT

    @property
    def value(self) -> OkT:
        return self._value

    def map(self, func: t.Callable[[OkT], OutT]) -> Result[OutT, ErrT]:
        return Ok(func(self.value))

    def apply(self, func: Result[t.Callable[[OkT], OutT], ErrT]) -> Result[OutT, ErrT]:
        match func:
            case Ok(f):
                return self.map(f)
            case Err(err):
                return Err(err)

    def bind(self, func: t.Callable[[OkT], Result[OutT, ErrT]]) -> Result[OutT, ErrT]:
        return func(self.value)


@dataclass
class Err(_ResultInternal[OkT, ErrT]):
    _value: ErrT

    @property
    def value(self) -> ErrT:
        return self._value

    def map(self, func: t.Callable[[OkT], OutT]) -> Result[OutT, ErrT]:
        return Err(self.value)

    def apply(self, func: Result[t.Callable[[OkT], OutT], ErrT]) -> Result[OutT, ErrT]:
        return Err(self.value)

    def bind(self, func: t.Callable[[OkT], Result[OutT, ErrT]]) -> Result[OutT, ErrT]:
        return Err(self.value)


Result = Ok[OkT, ErrT] | Err[OkT, ErrT]


def either(
    res: Result[OkT, ErrT],
    ok_func: t.Callable[[OkT], OutT],
    err_func: t.Callable[[ErrT], OutT],
) -> OutT:
    match res:
        case Ok(val):
            return ok_func(val)
        case Err(err):
            return err_func(err)


def safe(func: t.Callable[P, OutT]) -> t.Callable[P, Result[OutT, Exception]]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[OutT, Exception]:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as exc:
            return Err(exc)

    return wrapper
