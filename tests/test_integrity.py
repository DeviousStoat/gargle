import inspect
import typing as t

from gargle import maybe, result


def _integrity_check(classes: list[t.Any], ignore: list[str] = []) -> None:
    funcs = [dict(inspect.getmembers(c, predicate=inspect.isfunction)) for c in classes]
    for f in funcs:
        assert f.keys() == funcs[0].keys(), f"{f.keys()} != {funcs[0].keys()}"

        for x in f:
            if x in ignore:
                continue

            assert t.get_type_hints(funcs[0][x]) == t.get_type_hints(
                f[x]
            ), f"Function `{f[x].__name__}`"


def test_maybe_integrity() -> None:
    _integrity_check([maybe.Some, maybe.Nothing], ignore=["__init__"])


def test_result_integrity() -> None:
    _integrity_check([result.Ok, result.Err], ignore=["__init__"])
