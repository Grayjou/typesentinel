import pytest
import asyncio
from ..typesentinel.decorator import type_check, TypeCheck, ArgKind

def test_missing_keyword_argument_raises_type_error():
    @type_check(a=int)
    def fn(a): return a

    with pytest.raises(TypeError):
        #  python's check precedes decorator checks, raises TypeError instead of KeyError
        fn()  # missing 'a' # type: ignore

def test_multiple_checks_list():
    checks = [
        TypeCheck("x", int, ArgKind.KEYWORD),
        TypeCheck("y", str, ArgKind.KEYWORD),
    ]

    @type_check(checks)
    def fn(x, y):
        return x, y

    fn(1, "hello")

    with pytest.raises(TypeError):
        fn("nope", "hello")

    with pytest.raises(TypeError):
        fn(1, 2)

def test_positional_only_parameters():
    @type_check # type: ignore
    def fn(a: int, /, b: str):
        return True

    fn(10, "ok")

    with pytest.raises(TypeError):
        fn("bad", "ok")

def test_annotation_default_uses_default_kwarg_typecheck():
    @type_check # type: ignore
    def fn(a: int = 10):
        return True

    fn()
    fn(5)
    with pytest.raises(TypeError):
        fn("oops")
