import pytest
import asyncio
from type_check.type_checking.decorator import type_check

@pytest.mark.asyncio
async def test_async_function_type_checking():
    @type_check(a=int)
    async def fn(a):
        return a * 2

    assert await fn(5) == 10

    with pytest.raises(TypeError):
        await fn("oops")

@pytest.mark.asyncio
async def test_async_failure_handler():
    async def handler(*fails):
        raise TypeError("async fail")

    @type_check(a=int, on_failure=handler)
    async def fn(a):
        return a

    with pytest.raises(TypeError) as exc:
        await fn("oops")

    assert str(exc.value) == "async fail"
