from ..pytype_check.decorator import type_check
from ..pytype_check.type_check import TypeCheck, TypeCheckResult

def test_custom_handler_receives_failures():
    captured = {}

    def handler(*fails: TypeCheckResult):
        captured["msg"] = str(fails[0].type_check.name)

    @type_check(a=int, on_failure=handler)
    def fn(a):
        return a

    fn("bad")

    assert captured["msg"] == "a"
