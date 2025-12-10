# decorator.py
from __future__ import annotations
from .type_check import (
    TypeCheck,
    DefaultTypeCheckKwarg,
    ArgKind,
    TypeCheckResult,
)
from functools import wraps
from typing import Callable, Type, Any, Awaitable
import inspect
from dataclasses import dataclass


@dataclass
class TypeCheckContext:
    """Context for type checking that includes all relevant information."""
    func: Callable
    args: tuple
    kwargs: dict
    signature: inspect.Signature
    bound_args: inspect.BoundArguments
    all_results: list[TypeCheckResult]
    failed_results: list[TypeCheckResult]
    arg_names: list[str]
    
    @property
    def passed_results(self) -> list[TypeCheckResult]:
        """Get all passed type check results."""
        return [r for r in self.all_results if r.passed]


def default_on_type_check_failure(context: TypeCheckContext) -> None:
    """Default behavior on type check failure: raise TypeError with details."""
    if not context.failed_results:
        return

    first = context.failed_results[0]
    tc = first.type_check
    value = first.value

    # Use TypeCheck.message format
    base = tc.message
    raise TypeError(f"{base}, got {type(value).__name__}")


# Allow global override
type_check_default_handler = default_on_type_check_failure


class TypeCheckDecorator:
    """Core decorator implementation with async support."""
    
    def __init__(
        self,
        type_checks: TypeCheck | dict | list | None,
        kw_shorthand: dict[str, Type],
        on_failure: Callable | None = None
    ):
        self.normalized_checks = self._normalize_checks(type_checks, kw_shorthand)
        self.on_failure = on_failure
        self._signature_cache = {}
    
    def _normalize_checks(
        self,
        type_checks: TypeCheck | dict | list | None,
        kw_shorthand: dict[str, Type]
    ) -> list[TypeCheck]:
        """Normalize type checks from various input formats."""
        normalized = []
        
        if isinstance(type_checks, TypeCheck):
            normalized.append(type_checks)
        elif isinstance(type_checks, dict):
            normalized.append(TypeCheck.from_dict(type_checks))
        elif isinstance(type_checks, list):
            for item in type_checks:
                if isinstance(item, TypeCheck):
                    normalized.append(item)
                elif isinstance(item, dict):
                    normalized.append(TypeCheck.from_dict(item))
                else:
                    raise TypeError(f"Invalid type_checks entry: {type(item)}")
        elif type_checks is not None:
            raise TypeError("type_checks must be a TypeCheck, dict, list, or None")
        
        # Add shorthand keyword types
        for key, expected in kw_shorthand.items():
            normalized.append(DefaultTypeCheckKwarg.from_pair(key, expected))
        
        return normalized
    
    def _get_signature(self, func: Callable) -> inspect.Signature:
        """Cache signatures to avoid repeated inspection."""
        if func not in self._signature_cache:
            self._signature_cache[func] = inspect.signature(func)
        return self._signature_cache[func]
    
    def _rename_check_if_needed(self, tc: TypeCheck, arg_names: list[str]) -> TypeCheck:
        """
        Rename TypeCheck to use parameter name if it doesn't have a custom name.
        Only called right before validation when we know argument names.
        """
        # If TypeCheck already has a custom name, keep it
        if tc.name is not None and tc.name != str(tc.key):
            return tc
        
        if tc.arg_kind == ArgKind.POSITIONAL and isinstance(tc.key, int):
            if 0 <= tc.key < len(arg_names):
                param_name = arg_names[tc.key]
                return tc.copy_with(name=param_name)
        
        if tc.arg_kind == ArgKind.KEYWORD:
            return tc.copy_with(name=str(tc.key))
        
        return tc
    
    def _resolve_argument_value(
        self,
        tc: TypeCheck,
        bound_arguments: dict[str, Any],
        arg_names: list[str]
    ) -> Any:
        """Resolve argument value based on type check kind."""
        if tc.arg_kind == ArgKind.POSITIONAL:
            try:
                param_name = arg_names[int(tc.key)]
            except IndexError:
                raise IndexError(
                    f"TypeCheck refers to positional index {tc.key}, "
                    f"but only {len(arg_names)} args were passed."
                )
            return bound_arguments[param_name]
        
        elif tc.arg_kind == ArgKind.KEYWORD:
            if tc.key not in bound_arguments:
                if isinstance(tc, DefaultTypeCheckKwarg):
                    raise ValueError("DefaultTypeCheckKwarg should skip missing args")
                raise KeyError(
                    f"Expected keyword '{tc.key}', but it was not provided."
                )
            return bound_arguments[tc.key]
        
        raise ValueError(f"Unknown ArgKind: {tc.arg_kind}")
    
    def _validate_arguments(
        self,
        bound_arguments: dict[str, Any],
        arg_names: list[str]
    ) -> tuple[list[TypeCheckResult], list[TypeCheckResult]]:
        """Validate all arguments and return (all_results, failed_results)."""
        failures: list[TypeCheckResult] = []
        
        for tc in self.normalized_checks:
            # Rename check right before validation (minimal, localized change)
            renamed_tc = self._rename_check_if_needed(tc, arg_names)
            
            if tc.arg_kind == ArgKind.KEYWORD and isinstance(tc, DefaultTypeCheckKwarg):
                # Skip validation if keyword is missing (has default)
                if tc.key not in bound_arguments:
                    continue
            
            try:
                value = self._resolve_argument_value(tc, bound_arguments, arg_names)
                renamed_tc.validate(value)
                failures.append(TypeCheckResult(renamed_tc, value, True))
            except Exception:
                failures.append(TypeCheckResult(renamed_tc, value, False))
        
        failed = [r for r in failures if not r.passed]
        return failures, failed
    
    def _create_context(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        signature: inspect.Signature,
        bound_args: inspect.BoundArguments,
        all_results: list[TypeCheckResult],
        failed_results: list[TypeCheckResult],
        arg_names: list[str]
    ) -> TypeCheckContext:
        """Create a TypeCheckContext with all relevant information."""
        return TypeCheckContext(
            func=func,
            args=args,
            kwargs=kwargs,
            signature=signature,
            bound_args=bound_args,
            all_results=all_results,
            failed_results=failed_results,
            arg_names=arg_names
        )
    
    def _handle_failures(self, context: TypeCheckContext) -> None:
        """Call appropriate failure handler."""
        if context.failed_results:
            handler = self.on_failure or type_check_default_handler
            handler(context)
    
    async def _handle_failures_async(self, context: TypeCheckContext) -> None:
        """Call appropriate failure handler for async context."""
        if context.failed_results:
            handler = self.on_failure or type_check_default_handler
            
            if inspect.iscoroutinefunction(handler):
                await handler(context)
            else:
                handler(context)
    
    def _create_wrapper(self, func: Callable) -> Callable:
        """Create appropriate wrapper based on function type."""
        signature = self._get_signature(func)
        is_func_async = inspect.iscoroutinefunction(func)
        is_handler_async = self.on_failure and inspect.iscoroutinefunction(self.on_failure)
        
        if is_func_async or is_handler_async:
            return self._create_async_wrapper(func, signature, is_func_async)
        else:
            return self._create_sync_wrapper(func, signature)
    
    def _create_sync_wrapper(self, func: Callable, signature: inspect.Signature) -> Callable:
        """Create synchronous wrapper."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            
            arg_names = list(bound.arguments.keys())
            all_results, failed_results = self._validate_arguments(bound.arguments, arg_names)
            
            if failed_results:
                context = self._create_context(
                    func=func,
                    args=args,
                    kwargs=kwargs,
                    signature=signature,
                    bound_args=bound,
                    all_results=all_results,
                    failed_results=failed_results,
                    arg_names=arg_names
                )
                self._handle_failures(context)
                return
            return func(*args, **kwargs)
        
        return wrapper
    
    def _create_async_wrapper(
        self,
        func: Callable,
        signature: inspect.Signature,
        is_func_async: bool
    ) -> Callable:
        """Create asynchronous wrapper."""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            
            arg_names = list(bound.arguments.keys())
            all_results, failed_results = self._validate_arguments(bound.arguments, arg_names)
            
            if failed_results:
                context = self._create_context(
                    func=func,
                    args=args,
                    kwargs=kwargs,
                    signature=signature,
                    bound_args=bound,
                    all_results=all_results,
                    failed_results=failed_results,
                    arg_names=arg_names
                )
                await self._handle_failures_async(context)
                return
            if is_func_async:
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        return async_wrapper
    
    def __call__(self, func: Callable) -> Callable:
        """Apply type checking to function."""
        return self._create_wrapper(func)


def type_check(
    type_checks: TypeCheck | dict | list | None = None,
    *,
    on_failure: Callable | None = None,
    **kw_expected_types: Type
) -> Callable:
    """
    Decorator supporting:
    - @type_check
    - @type_check(...)
    - @type_check(a=int, b=str)
    - @type_check(on_failure=handler)
    """
    
    # CASE A — used without parentheses: @type_check
    if callable(type_checks) and not kw_expected_types and on_failure is None:
        func = type_checks
        return _apply_annotation_type_checks(func)
    
    # CASE B — used with params
    decorator = TypeCheckDecorator(
        type_checks=type_checks,
        kw_shorthand=kw_expected_types,
        on_failure=on_failure,
    )
    
    # Return decorator that will be applied to function
    def decorator_wrapper(func: Callable) -> Callable:
        return decorator(func)
    
    return decorator_wrapper


def _apply_annotation_type_checks(func: Callable) -> Callable:
    """Apply type checks based on function annotations."""
    signature = inspect.signature(func)
    checks = []
    
    for idx, (param_name, param) in enumerate(signature.parameters.items()):
        if param.annotation is inspect._empty:
            continue  # no annotation → skip
        
        expected = param.annotation
        
        # Keyword-only or named parameters
        if param.kind in (param.KEYWORD_ONLY, param.POSITIONAL_OR_KEYWORD):
            if param.default is inspect._empty:
                checks.append(TypeCheck(param_name, expected, arg_kind=ArgKind.KEYWORD, name=param_name))
            else:
                # Has default → behave like DefaultTypeCheckKwarg
                checks.append(DefaultTypeCheckKwarg.from_pair(param_name, expected))
        
        # Positional-only parameters
        elif param.kind == param.POSITIONAL_ONLY:
            checks.append(TypeCheck(idx, expected, arg_kind=ArgKind.POSITIONAL, name=param_name))
    
    # Create decorator with annotation-derived checks
    decorator = TypeCheckDecorator(type_checks=checks, kw_shorthand={})
    return decorator(func)