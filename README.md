# pytype_check

`pytype_check` provides small, dependency-free helpers for runtime validation of function
arguments. Decorate any synchronous or asynchronous function to validate positional or
keyword arguments using type hints, explicit `TypeCheck` objects, or keyword shorthand.

## Installation

```bash
pip install pytype-check
```

## Quick start

Use the `type_check` decorator to enforce annotations automatically or pass explicit
types as keyword arguments:

```python
from pytype_check.decorator import type_check

@type_check  # pulls types from annotations
def greet(name: str, excited: bool = False) -> str:
    return f"Hello, {name}{'!' if excited else ''}"

@type_check(name=str, times=int)  # shorthand keyword type checks
async def repeat(name: str, times: int):
    return ", ".join(name for _ in range(times))
```

Passing values that fail validation raises a `TypeError` with a clear message such as
`Invalid type for argument 'name': expected str, got int`.

## Customizing failure handling

Provide an `on_failure` callback to intercept failed checks. The handler receives one or
more `TypeCheckResult` instances and can raise, log, or transform the error:

```python
from pytype_check.decorator import type_check
from pytype_check.type_check import TypeCheckResult

failures = []

async def capture(*results: TypeCheckResult):
    failures.extend(results)
    # raise a custom error instead of the default TypeError
    raise ValueError("validation failed")

@type_check(a=int, on_failure=capture)
async def double(a: int) -> int:
    return a * 2
```

Both synchronous and asynchronous handlers are supported. If you omit `on_failure`, a
`TypeError` is raised using the message configured on each `TypeCheck`.

## Using explicit `TypeCheck` objects

You can define checks manually for more control over argument kinds and error text:

```python
from pytype_check.decorator import type_check
from pytype_check.type_check import TypeCheck, ArgKind

checks = [
    TypeCheck(0, int, arg_kind=ArgKind.POSITIONAL),
    TypeCheck("label", str, arg_kind=ArgKind.KEYWORD, message="label must be a string"),
]

@type_check(checks)
def render(value, *, label):
    return f"{label}: {value}"
```

## Development

After cloning the repository you can run the test suite with:

```bash
python -m pytest
```

The project is distributed under the MIT License.
