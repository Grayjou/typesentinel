from ..pytype_check.type_check import TypeCheck, ArgKind, valid_arg_kind_map
from typing import Callable, Union
import pytest

def test_individual_checks():
    tc1 = TypeCheck(key=0, expected_type=int, arg_kind=ArgKind.POSITIONAL)
    assert tc1.validate(5) == 5

    tc2 = TypeCheck(key="name", expected_type=str, arg_kind=ArgKind.KEYWORD)
    assert tc2.validate("test") == "test"
    with pytest.raises(TypeError) as exc:
        tc1.validate("not an int")

    assert str(exc.value) == "Invalid type for argument '0': expected int, got str"

    with pytest.raises(TypeError) as exc:
        tc2.validate(123)
    assert str(exc.value) == "Invalid type for argument 'name': expected str, got int"

def test_invalid_arg_kind_pair_raises():
    with pytest.raises(ValueError) as exc:
        TypeCheck(key="0", expected_type=int, arg_kind=ArgKind.POSITIONAL)
    assert str(exc.value) == "positional arguments require a int key, got str"

    with pytest.raises(ValueError) as exc:
        TypeCheck(key=1, expected_type=str, arg_kind=ArgKind.KEYWORD)
    assert str(exc.value) == "keyword arguments require a str key, got int"

def test_type_check_from_dict():
    tc_dict = {
        "key": "age",
        "expected_type": int,
        "arg_kind": ArgKind.KEYWORD,
        "message": "Age must be an integer",
        "name": "age"
    }
    tc = TypeCheck.from_dict(tc_dict)
    assert tc.key == "age"
    assert tc.expected_type == int
    assert tc.arg_kind == ArgKind.KEYWORD
    assert tc.message == "Age must be an integer"

def test_type_check_union_type():
    tc = TypeCheck(key=0, expected_type= Union[int, str], arg_kind=ArgKind.POSITIONAL)
    assert tc.validate(10) == 10
    assert tc.validate("hello") == "hello"
    with pytest.raises(TypeError) as exc:
        tc.validate(5.5)
    assert str(exc.value) == "Invalid type for argument '0': expected int | str, got float"

def test_type_check_pep604_union():
    tc = TypeCheck(key="value", expected_type= int | str, arg_kind=ArgKind.KEYWORD)
    assert tc.validate(20) == 20
    assert tc.validate("world") == "world"
    with pytest.raises(TypeError) as exc:
        tc.validate(3.14)
    assert str(exc.value) == "Invalid type for argument 'value': expected int | str, got float"