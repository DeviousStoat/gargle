# import typing as t
# from dataclasses import dataclass

# from gargle.maybe import (
# Maybe, Nothing, Some, as_maybe, is_nothing, is_some, maybe_get
# )
# from gargle.result import Err, Ok, Result
# from gargle.typeclasses import Applicative, Functor

# T = t.TypeVar("T")


# @dataclass
# class Blop1:
#     x: int


# @dataclass
# class Blop2:
#     y: Blop1 | None = None


# b = Blop2(y=Blop1(5))
