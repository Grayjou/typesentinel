from ..type_checking.type_check import TypeCheck, ArgKind, valid_arg_kind_map
from typing import Callable

def test_individual_checks():
    tc1 = TypeCheck(key=0, expected_type=int, arg_kind=ArgKind.POSITIONAL)
    assert tc1.validate(5) == 5

    tc2 = TypeCheck(key="name", expected_type=str, arg_kind=ArgKind.KEYWORD)
    assert tc2.validate("test") == "test"

    try:
        tc1.validate("not an int")
    except TypeError as e:
        assert str(e) == "argument '0' must be int, got str"

    try:
        tc2.validate(123)
    except TypeError as e:
        assert str(e) == "argument 'name' must be str, got int"