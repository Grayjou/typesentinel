"""Public interface for the :mod:`typesentinel` package.

This module gathers the most commonly used decorators and helpers so users can
import them directly from ``typesentinel`` without reaching into submodules.
"""
from .decorator import (
    TypeCheckDecorator,
    default_on_type_check_failure,
    type_check,
    type_check_default_handler,
)
from .type_check import ArgKind, DefaultTypeCheckKwarg, TypeCheck, TypeCheckResult, get_type_name

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

__version__ = "0.2.1"
