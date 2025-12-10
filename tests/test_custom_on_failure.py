from ..typesentinel.decorator import type_check, TypeCheckContext
from ..typesentinel.type_check import TypeCheck, TypeCheckResult
import pytest
def test_custom_handler_receives_failures():
    captured = {}

    def handler(context:TypeCheckContext):
        captured["msg"] = str(context.failed_results[0].type_check.name)

    @type_check(a=int, on_failure=handler)
    def fn(a):
        return a

    fn("bad")

    assert captured["msg"] == "a"

def test_custom_handler_receives_multiple_failures():
    captured = {}

    def handler(context:TypeCheckContext):
        msgs = [str(f.type_check.name) for f in context.failed_results]
        captured["msgs"] = msgs

    @type_check(a=int, b=str, on_failure=handler)
    def fn(a, b):
        return a, b

    fn("bad", 123)

    assert captured["msgs"] == ["a", "b"]

@pytest.mark.asyncio
async def test_async_custom_handler_receives_failures():
    captured = {}

    async def handler(context:TypeCheckContext):
        captured["msg"] = str(context.failed_results[0].type_check.name)

    @type_check(a=int, on_failure=handler)
    async def fn(a):
        return a

    await fn("bad")

    assert captured["msg"] == "a"

def test_custom_handler_gets_full_context():
    captured = {}

    def handler(context:TypeCheckContext):
        captured["all"] = context.all_results
        captured["failed"] = context.failed_results
        captured["args"] = context.args
        captured["kwargs"] = context.kwargs
    @type_check(a=int, b=str, on_failure=handler)
    def fn(a, b):
        return a, b

    fn("bad", 123)

    assert len(captured["all"]) == 2
    assert len(captured["failed"]) == 2
    assert all(isinstance(r, TypeCheckResult) for r in captured["all"])
    assert all(isinstance(r, TypeCheckResult) for r in captured["failed"])
    assert captured["args"] == ("bad", 123)
    assert captured["kwargs"] == {}

def test_custom_handler_prevents_execution():
    anger_level = {"level": 0}

    def handler(context:TypeCheckContext):
        anger_level["level"] += 1

    @type_check(a=int, on_failure=handler)
    def fn(a):
        return a

    result = fn("bad")

    assert anger_level["level"] == 1
    assert result is None