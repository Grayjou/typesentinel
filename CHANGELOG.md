
# 📦 Changelog

## **0.2.2 – Enhanced failure-handling API & internal refactor**

*(Re-release after yanked versions 0.2.0–0.2.1)*

### 🎯 Overview

This release introduces a richer, structured failure-handling API via a new `TypeCheckContext` object. Handlers (sync or async) now receive full contextual information about the call, including all type-check results, instead of receiving only the raw failures list. Decorator internals were refactored to support this cleanly.

### ✨ What’s New

#### **🔹 New `TypeCheckContext` dataclass**

Handlers now receive a single context object with:

* `func`: original function
* `args` / `kwargs`: raw call arguments
* `signature` / `bound_args`: inspect metadata
* `all_results`: all `TypeCheckResult` objects
* `failed_results`: list of failures
* `arg_names`: ordered argument names
* `passed_results` property

This gives custom handlers complete insight into the call and validation.

#### **🔹 Updated default failure handler**

`default_on_type_check_failure` switched to accept a `TypeCheckContext` instead of variadic results.

It still raises a `TypeError` by default, but now has access to full context.

#### **🔹 Updated custom handler calling convention**

Custom `on_failure` handlers now receive **one argument**:

```py
def my_handler(context: TypeCheckContext):
    ...
```

Async handlers are awaited automatically.

#### **🔹 Synchronous & asynchronous wrappers updated**

Both sync and async decorator wrappers now:

1. run validation
2. construct a `TypeCheckContext`
3. call the handler with the context

No more passing `*failures`.

#### **🔹 Test suite update**

`tests/test_custom_on_failure.py` updated to use:

```py
def handler(context: TypeCheckContext):
    ...
```

instead of `*failures`.

Internal behavior is now consistent and easier to extend.

### 🛠 Internal Refactors

* Added `_create_context(...)` helper to build `TypeCheckContext` instances cleanly.
* Merged duplicated failure-handling logic into context-based versions (`_handle_failures` + `_handle_failures_async`).
* Improved separation between validation and handler invocation.
* Updated imports to expose `TypeCheckContext`.

### 📁 File Changes Summary

* `pyproject.toml`: version bumped → `0.2.2`
* `test_custom_on_failure.py`: adjusted handler signature
* `decorator.py`: major refactor (≈80 added lines, 14 removed)

  * added `TypeCheckContext`
  * updated default handler
  * updated sync/async handling logic
  * centralized context construction

---

## **0.2.0 – Initial release**

0.2.0 – Initial release
🎯 Overview
First public release of typesentinel, a lightweight, dependency-free library for runtime type checking of Python function arguments, with support for both synchronous and asynchronous functions.

✨ Features
Runtime type-checking decorator @type_check for validating function arguments at call time.

Works with:

Function annotations (@type_check bare usage)
Shorthand keyword arguments (@type_check(a=int, b=str))
Explicit TypeCheck objects and lists.
Async support

Fully supports decorating async def functions.
Supports async on_failure handlers (awaited when needed).
Union and complex types

Handles typing.Union and PEP 604 unions (int | str), with human-readable type names in errors.
Clear, parameter-aware error messages

Errors include the real parameter name (even when checks are defined positionally).
Centralized message formatting via TypeCheck.message / error_message.
Configurable failure handling

Default behavior raises TypeError with a detailed message.
Custom on_failure callback (sync or async) via decorator argument.
Support for defaulted keyword arguments

DefaultTypeCheckKwarg skips validation when the keyword isn’t provided, enabling optional parameters that are only validated when passed explicitly.
Explicit TypeCheck model

TypeCheck dataclass encapsulating:

target key (positional index or keyword name)
expected type (including unions)
argument kind (ArgKind.POSITIONAL / ArgKind.KEYWORD)
optional custom message and display name.
No magic / no globals

Works only where explicitly applied; no monkey-patching, no global interception of calls.
Zero dependencies & typed

No runtime dependencies, typed codebase with Typing :: Typed classifier.
Tested

Includes pytest test suite covering core decorator behavior, async cases, custom handlers, and extended scenarios.
🧩 Internals (high level)
Core logic implemented in:

typesentinel.decorator – decorator orchestration, async/sync wrappers, failure handling.
typesentinel.type_check – TypeCheck, DefaultTypeCheckKwarg, TypeCheckResult, and type name formatting helpers.