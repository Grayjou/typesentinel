
# pytype-check


**pytype-check** is a lightweight, dependency-free library for **runtime type checking**
of Python function arguments. It supports both synchronous and asynchronous functions,
Union types, custom failure handlers, and signature-aware error messages.

```bash
pip install pytype-check
````

---

## 🧠 Why `pytype-check`?

Other libraries like Pydantic, Beartype, Enforce, or typeguard offer runtime validation,
but often come with heavy dependencies, global monkey-patching, performance costs, or
complicated configuration.

`pytype-check` focuses on **one thing** and does it well:

* ✔ **Minimal** — zero dependencies, tiny footprint
* ✔ **Explicit** — works only where you decorate; never global
* ✔ **Async-friendly** — supports async functions & async failure handlers
* ✔ **Precise errors** — error messages include the real parameter names
* ✔ **Flexible** — annotations, shorthand, or explicit `TypeCheck` objects
* ✔ **Safe** — never mutates your function’s signature or typing info

If you want simple, predictable runtime validation with no overhead,
**pytype-check is built for you.**

---

## 🚀 Quick Start

### Type checking from function annotations

```python
from pytype_check.decorator import type_check

@type_check
def greet(name: str, excited: bool = False):
    return f"Hello, {name}{'!' if excited else ''}"

greet("Alice")       # OK
greet(123)           # ❌ Invalid type for argument 'name': expected str, got int
```

### Shorthand keyword type checks

```python
@type_check(name=str, times=int)
async def repeat(name, times):
    return ", ".join(name for _ in range(times))
```

---

## 🔍 Union Type Support

```python
from typing import Union

@type_check(a=Union[int, str])
def fn(a):
    return a

@type_check(a=int | str)
def fn(a):
    return a
```

Error message:

```
Invalid type for argument 'a': expected int | str, got float
```

---

## 🛠 Custom Failure Handling

```python
from pytype_check.decorator import type_check
from pytype_check.type_check import TypeCheckResult

async def capture(*fails: TypeCheckResult):
    raise ValueError("validation failed")

@type_check(a=int, on_failure=capture)
async def double(a):
    return a * 2
```

---

## 🧩 Explicit TypeCheck Objects

```python
from pytype_check.decorator import type_check
from pytype_check.type_check import TypeCheck, ArgKind

checks = [
    TypeCheck(0, int, ArgKind.POSITIONAL),
    TypeCheck("label", str, ArgKind.KEYWORD, message="label must be a string"),
]

@type_check(checks)
def render(value, *, label):
    return f"{label}: {value}"
```

---

## 🧪 Testing

```bash
python -m pytest
```

---

## 📄 License

MIT License. See `LICENSE` for details.

```

---
