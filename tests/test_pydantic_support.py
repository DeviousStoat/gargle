import pytest
from pydantic import BaseModel, ValidationError

from gargle.maybe import Maybe, Nothing, Some


class TestMaybePydantic:
    class Model1(BaseModel):
        s: Maybe[str]
        x: Maybe[int]

    def test_regular_build_works(self):
        m = self.Model1(s=Some("hello"), x=Nothing())

        assert m.s == Some("hello")
        assert m.x == Nothing()

    # def test_optional_to_maybe(self):
    #     m = self.Model1(s="hello", x=None)  # type: ignore

    #     assert m.s == Some("hello")
    #     assert m.x == Nothing()

    def test_validate_wrong_type(self):
        with pytest.raises(ValidationError) as exc_info:
            self.Model1(s=Some({}), x=Some([]))  # type: ignore

        assert [e["msg"] for e in exc_info.value.errors()] == [
            "str type expected",
            "value is not a valid integer",
        ]
