import pytest
from ..pytype_check.type_check import TypeCheck, DefaultTypeCheckKwarg, ArgKind

def test_custom_message_used():
    tc = TypeCheck("age", int, ArgKind.KEYWORD, message="Age must be integer")
    with pytest.raises(TypeError) as exc:
        tc.validate("not an int")
    assert str(exc.value) == "Age must be integer, got str"

def test_default_kwarg_skips_when_missing():
    tc = DefaultTypeCheckKwarg.from_pair("age", int)
    # simulate missing argument
    assert tc.validate_missing() is True

def test_default_kwarg_valid_when_present():
    tc = DefaultTypeCheckKwarg.from_pair("age", int)
    assert tc.validate(20) == 20
    with pytest.raises(TypeError):
        tc.validate("oops")

def test_typecheck_from_dict_errors():
    with pytest.raises(TypeError):
        TypeCheck.from_dict({"key": 0, "expected_type": str, "arg_kind": 123})  # invalid kind
