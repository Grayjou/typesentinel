"""Compatibility facade to expose :mod:`typesentinel` from the repository root.

Keeping these re-exports allows ``import pytype_check`` workflows to continue to
function while the installable package remains ``typesentinel``.
"""
from .typesentinel import (
    ArgKind,
    DefaultTypeCheckKwarg,
    TypeCheck,
    TypeCheckDecorator,
    TypeCheckResult,
    default_on_type_check_failure,
    get_type_name,
    type_check,
    type_check_default_handler,
)

__all__ = [
    "ArgKind",
    "DefaultTypeCheckKwarg",
    "TypeCheck",
    "TypeCheckDecorator",
    "TypeCheckResult",
    "default_on_type_check_failure",
    "get_type_name",
    "type_check",
    "type_check_default_handler",
]
