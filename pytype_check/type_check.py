from __future__ import annotations
from typing import Type, Optional, Any
from dataclasses import dataclass
from enum import Enum
from typing import get_origin, get_args, Union
from types import UnionType
import types

TypeKey = str | int


class ArgKind(Enum):
    POSITIONAL = "positional"
    KEYWORD = "keyword"


valid_arg_kind_map = {
    ArgKind.POSITIONAL: int,
    ArgKind.KEYWORD: str,
}

def get_type_name(tp: Type | UnionType) -> str:
    """
    Return a human-readable type name for hints, unions, generics, etc.
    Always safe — never depends on tp.__name__ existing.
    """
    origin = get_origin(tp)
    args = get_args(tp)

    # Case 1 — real Python type (int, str, list, dict, etc.)
    if isinstance(tp, type):
        return tp.__name__

    # Case 2 — typing.Union or PEP 604 union (X | Y)
    if origin is Union or origin is types.UnionType:
        return " | ".join(get_type_name(a) for a in args)

    # Case 3 — parametrized generics (list[int], dict[str, int], etc.)
    if origin:
        base = origin.__name__
        inner = ", ".join(get_type_name(a) for a in args)
        return f"{base}[{inner}]"

    # Fallback — best-effort string
    return str(tp)


@dataclass(frozen=True)
class TypeCheck:
    key: TypeKey
    expected_type: Type | UnionType
    arg_kind: ArgKind = ArgKind.POSITIONAL
    message: Optional[str] = None
    name: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.key, (str, int)):
            raise TypeError("key must be str or int")

        origin = get_origin(self.expected_type)

        # Allow: real Python types, PEP 604 unions, typing.Union
        if not (
            isinstance(self.expected_type, type)
            or origin is Union
            or origin is types.UnionType
        ):
            raise TypeError("expected_type must be a Python type or Union")


        expected_key_type = valid_arg_kind_map[self.arg_kind]
        if not isinstance(self.key, expected_key_type):
            raise ValueError(
                f"{self.arg_kind.value} arguments require a {expected_key_type.__name__} key, "
                f"got {type(self.key).__name__}"
            )

        if self.name is None:
            object.__setattr__(self, "name", str(self.key))
        expected_name = get_type_name(self.expected_type)
        if self.message is None:
            object.__setattr__(
                self,
                "message",
                f"Invalid type for argument '{self.name}': expected {expected_name}",
            )



    def validate(self, value):
        origin = get_origin(self.expected_type)
        if origin is Union or origin is types.UnionType:
            # isinstance allows a tuple of types
            if not isinstance(value, get_args(self.expected_type)):
                raise TypeError(self.error_message(type(value)))
            return value
        
        # normal case
        if not isinstance(value, self.expected_type):
            raise TypeError(self.error_message(type(value)))
        return value


    @classmethod
    def from_dict(cls, data: dict) -> "TypeCheck":
        raw_kind = data.get("arg_kind", ArgKind.POSITIONAL)

        if isinstance(raw_kind, str):
            arg_kind = ArgKind(raw_kind)
        elif isinstance(raw_kind, ArgKind):
            arg_kind = raw_kind
        else:
            raise TypeError(f"Invalid arg_kind value: {raw_kind}")

        return cls(
            key=data["key"],
            expected_type=data["expected_type"],
            arg_kind=arg_kind,
            message=data.get("message"),
            name=data.get("name"),
        )
    
    def error_message(self, actual_type: Type) -> str:
        return f"{self.message}, got {actual_type.__name__}"


class DefaultTypeCheckKwarg(TypeCheck):
    """
    TypeCheck that *skips validation if the keyword argument is missing*.
    """
    @classmethod
    def from_pair(cls, key: str, expected_type: Type):
        return cls(key=key, expected_type=expected_type, arg_kind=ArgKind.KEYWORD)

    def validate_missing(self) -> bool:
        """Return True meaning: skip validation."""
        return True


@dataclass(frozen=True)
class TypeCheckResult:
    """
    Represents the outcome of a single TypeCheck.
    """
    type_check: TypeCheck
    value: Any
    passed: bool

    def __repr__(self):
        status = "PASSED" if self.passed else "FAILED"
        return f"<TypeCheckResult {status} {self.type_check.name}={self.value!r}>"