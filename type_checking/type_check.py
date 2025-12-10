from __future__ import annotations
from typing import Type, Optional, Any
from dataclasses import dataclass
from enum import Enum


TypeKey = str | int


class ArgKind(Enum):
    POSITIONAL = "positional"
    KEYWORD = "keyword"


valid_arg_kind_map = {
    ArgKind.POSITIONAL: int,
    ArgKind.KEYWORD: str,
}


@dataclass(frozen=True)
class TypeCheck:
    key: TypeKey
    expected_type: Type
    arg_kind: ArgKind = ArgKind.POSITIONAL
    message: Optional[str] = None
    name: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.key, (str, int)):
            raise TypeError("key must be str or int")

        if not isinstance(self.expected_type, type):
            raise TypeError("expected_type must be a Python type")

        expected_key_type = valid_arg_kind_map[self.arg_kind]
        if not isinstance(self.key, expected_key_type):
            raise ValueError(
                f"{self.arg_kind.value} arguments require a {expected_key_type.__name__} key, "
                f"got {type(self.key).__name__}"
            )

        if self.name is None:
            object.__setattr__(self, "name", str(self.key))

        if self.message is None:
            object.__setattr__(
                self,
                "message",
                f"Invalid type for key '{self.name}': expected {self.expected_type.__name__}",
            )

    def validate(self, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"argument '{self.name}' must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
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