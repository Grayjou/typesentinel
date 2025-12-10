import asyncio
import pytest

from ..pytype_check.decorator import type_check


def test_async_function_type_checking():
    @type_check(a=int)
    async def fn(a):
        return a * 2

    assert asyncio.run(fn(5)) == 10

    with pytest.raises(TypeError):
        asyncio.run(fn("oops"))


def test_async_failure_handler():
    async def handler(*fails):
        raise TypeError("async fail")

    @type_check(a=int, on_failure=handler)
    async def fn(a):
        return a

    with pytest.raises(TypeError) as exc:
        asyncio.run(fn("oops"))

    assert str(exc.value) == "async fail"
