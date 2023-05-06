import inspect
import typing as t

from gargle import maybe, result


def _integrity_check(
    classes: list[t.Any], ignore_type_integrity_check: list[str] = []
) -> None:
    funcs = [dict(inspect.getmembers(c, predicate=inspect.isfunction)) for c in classes]
    for f in funcs:
        assert f.keys() == funcs[0].keys(), f"{f.keys()} != {funcs[0].keys()}"

        for x in f:
            assert funcs[0][x].__doc__ == f[x].__doc__, f"Function `{f[x].__name__}`"

            if x in ignore_type_integrity_check:
                continue

            assert t.get_type_hints(funcs[0][x]) == t.get_type_hints(
                f[x]
            ), f"Function `{f[x].__name__}`"


def test_maybe_integrity() -> None:
    _integrity_check(
        [maybe.Some, maybe.Nothing],
        ignore_type_integrity_check=["__init__", "from_maybe"],
    )


def test_result_integrity() -> None:
    _integrity_check([result.Ok, result.Err], ignore_type_integrity_check=["__init__"])
