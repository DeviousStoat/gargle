import pytest
from pydantic import BaseModel, ValidationError

from gargle.maybe import MaybeFromOptional, Nothing, Some, is_some


class Model1(BaseModel):
    s: MaybeFromOptional[str]
    x: MaybeFromOptional[int]


class Model2(BaseModel):
    model1: MaybeFromOptional[Model1]


class TestMaybePydantic:
    def test_regular_build(self):
        m = Model1(s=Some("hello"), x=Nothing[int]())

        assert m.s == Some("hello")
        assert m.x == Nothing()

    def test_nested(self):
        m = Model2(model1=Some(Model1(s=Some("hello"), x=Nothing[int]())))

        assert m.model1.and_then(lambda m1: m1.s) == Some("hello")
        assert m.model1.and_then(lambda m1: m1.x) == Nothing()

        m = Model2(model1=Model1(s="hello", x=5))  # type: ignore

        assert m.model1.and_then(lambda m1: m1.s) == Some("hello")
        assert m.model1.and_then(lambda m1: m1.x) == Some(5)

    def test_optional_to_maybe(self):
        m = Model1(s=None, x=None)  # type: ignore

        assert m.s == Nothing()
        assert m.x == Nothing()

    def test_optional_to_maybe_nested(self):
        m = Model2(model1=None)  # type: ignore

        assert m.model1 == Nothing()

        m = Model2(model1=Model1(s=None, x=Some(5)))  # type: ignore

        assert is_some(m.model1)
        assert m.model1.and_then(lambda m1: m1.s) == Nothing()
        assert m.model1.and_then(lambda m1: m1.x) == Some(5)

    def test_validate_wrong_type(self):
        with pytest.raises(ValidationError) as exc_info:
            Model1(s=Some({}), x=Some([]))  # type: ignore

        assert [e["msg"] for e in exc_info.value.errors()] == [
            "str type expected",
            "value is not a valid integer",
        ]
