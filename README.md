# resultpy

Lightweight Result type for Python, inspired by [better-result](https://github.com/dmmulroy/better-result).

## Install

```bash
pip install resultpy
```

## Quick Start

```python
from resultpy import Result, safe
import json

# Wrap throwing functions
def load_user() -> dict[str, str]:
    return json.loads('{"name": "John", "age": 30}')
parsed = safe(load_user)

# Check and use
if parsed.is_ok():
    print(parsed.unwrap())
else:
    print(parsed.unwrap_err())

# Or use pattern matching
message = parsed.match({
    "ok": lambda data: f"Got: {data['name']}",
    "err": lambda e: f"Failed: {e.cause}",
})
```

## Contents

- [Creating Results](#creating-results)
- [Transforming Results](#transforming-results)
- [Handling Errors](#handling-errors)
- [Extracting Values](#extracting-values)
- [Retry Support](#retry-support)
- [Generator Composition](#generator-composition) *(TODO)*
- [Tagged Errors](#tagged-errors) *(TODO)*
- [Serialization](#serialization) *(TODO)*
- [API Reference](#api-reference)

## Creating Results

```python
from resultpy import Result, Ok, Err, safe, safe_async

# Success
ok = Result.ok(42)

# Error
err = Result.err(ValueError("failed"))

# From throwing function
def risky() -> float:
    raise ValueError("Invalid input")

result = safe(risky)

# From async function
async def risky_async() -> float:
    raise ValueError("Invalid input")

result = await safe_async(risky_async)

# With custom error handling
result = safe({"try_": risky, "catch": lambda e: "Error: " + str(e)})
```

## Transforming Results

```python
from resultpy import Ok, Err, map as result_map

result = (
    Ok[int, ValueError](2)
    .map(lambda x: x * 2)  # Ok(4)
    .and_then(
        # Chain Result-returning functions
        lambda x: Ok[int, ValueError](x) if x > 0 else Err[int, ValueError](ValueError("negative"))
    )
)

# Standalone functions (data-first or data-last)
result_map(result, lambda x: x + 1)
result_map(lambda x: x + 1)(result)  # Pipeable
```

## Handling Errors

```python
from resultpy import Result, Err

err_result: Result[int, ValueError] = Err[int, ValueError](ValueError("invalid"))

# Transform errors
err_result.map_err(lambda e: RuntimeError(str(e)))  # Err(RuntimeError(...))

# Fallback values
err_result.unwrap_or(0)  # 0

# Pattern match
err_result.match({
    "ok": lambda x: f"Got {x}",
    "err": lambda e: f"Failed: {e}"
})


# Recover from specific errors
class NotFoundError(TaggedError):
    __slots__ = ("id",)
    @property
    def tag(self) -> str:
        return "NotFoundError"
    def __init__(self, id: str) -> None:
        super().__init__(f"Not found: {id}")
        self.id = id

def fetch_user(id: str) -> Result[dict[str, str], NotFoundError]:
    # Could return Ok(user) or Err(NotFoundError(id))
    if id == "valid":
        return Result.ok({"name": "John", "id": id})
    return Result.err(NotFoundError(id))

def recover_from_not_found(e: NotFoundError) -> Result[dict[str, str], NotFoundError]:
    return Result.ok({"name": "Default User"})

# Recover from specific errors
result = fetch_user("123").match({
    "ok": lambda user: Result.ok(user),  # Pass through success
    "err": lambda e: recover_from_not_found(e) if e.tag == "NotFoundError" else Result.err(e)
})


```

## Extracting Values

```python
from resultpy import Result, unwrap

result_ok = Result.ok(42)
result_err = Result.err(ValueError("invalid"))

# Unwrap (throws on Err)
value = unwrap(result_ok)
value = result_ok.unwrap()
value = result_ok.unwrap("custom error message")

# With fallback
value = result_err.unwrap_or(0)

# Pattern match
value = result_err.match({
    "ok": lambda v: v,
    "err": lambda e: 0,
})
```

## Retry Support

```python
from resultpy import safe, safe_async

def risky() -> float:
    raise ValueError("Invalid input")

# Sync retry
result = safe(risky, {"retry": {"times": 3}})

# Async retry with backoff
async def fetch(url: str) -> str:
    raise ConnectionError("Network error")

result = await safe_async(
    lambda: fetch("https://api.example.com"),
    {
        "retry": {
            "times": 3,
            "delay_ms": 100,
            "backoff": "exponential",  # or "linear" | "constant"
        }
    }
)
```

## Generator Composition

*TODO: Coming soon*

## Tagged Errors

```python
class NotFoundError(TaggedError):
    __slots__ = ("id",)
    @property
    def tag(self) -> str:
        return "NotFoundError"
    def __init__(self, id: str) -> None:
        super().__init__(f"Not found: {id}")
        self.id = id

class ValidationError(TaggedError):
    __slots__ = ("field",)
    @property
    def tag(self) -> str:
        return "ValidationError"
    def __init__(self, field: str) -> None:
        super().__init__(f"Invalid: {field}")
        self.field = field

AppError: TypeAlias = Union[NotFoundError, ValidationError] 

result_err = Result.err(ValidationError("name"))

def handle_validation_error(e: ValidationError) -> Result[dict[str, str], ValidationError]:
    return Result.ok({"message": f"Invalid: {e.field}"})
def handle_not_found_error(e: NotFoundError) -> Result[dict[str, str], NotFoundError]:
    return Result.ok({"name": "Default User"})

# Exhaustive matching
result_exhaustive = TaggedError.match(
    result_err.unwrap_err(),
    {
        ValidationError: handle_validation_error,
        NotFoundError: handle_not_found_error,
    }
)

# Partial matching with a fallback
result_partial = TaggedError.match_partial(
    result_err.unwrap_err(),
    {
        "ValidationError": handle_validation_error,
        "NotFoundError": handle_not_found_error,
    },
    otherwise=lambda: Result.ok({"message": "Unknown error"})
)

```


## Serialization

*TODO: Coming soon*

## API Reference

### Result

| Function | Description |
|----------|-------------|
| `Result.ok(value)` | Create success |
| `Result.err(error)` | Create error |
| `safe(fn, config?)` | Wrap throwing function with optional retry |
| `safe_async(fn, config?)` | Wrap async function with optional retry |
| `unwrap(result, message?)` | Extract value or raise |
| `map(result, fn)` | Transform success value (data-first) |
| `map(fn)(result)` | Transform success value (data-last) |

### Instance Methods

| Method | Description |
|--------|-------------|
| `.is_ok()` | Check if Ok |
| `.is_err()` | Check if Err |
| `.map(fn)` | Transform success value |
| `.map_err(fn)` | Transform error value |
| `.and_then(fn)` | Chain Result-returning function |
| `.and_then_async(fn)` | Chain async Result-returning function |
| `.match({"ok": fn, "err": fn})` | Pattern match |
| `.unwrap(message?)` | Extract value or raise |
| `.unwrap_or(fallback)` | Extract value or return fallback |
| `.unwrap_err(message?)` | Extract error or raise |
| `.tap(fn)` | Side effect on success |
| `.tap_async(fn)` | Async side effect on success |

## License

MIT
