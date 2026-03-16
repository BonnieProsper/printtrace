# printtrace

Thread-safe, contextual debug printing for Python.

`printtrace` is a deliberate middle ground between `print()` and `logging`:
- thread-safe
- ordered output across threads
- call-site context included automatically
- no configuration

## Why not logging?

Logging requires handlers, formatters, and configuration. `printtrace` requires nothing - import and call it.

## Installation

```bash
pip install printtrace
```

## Usage

```python
from printtrace import printtrace

printtrace("hello", {"a": 1})
```

Output:
```
[MainThread] app.py:42 in handler | 'hello' {'a': 1}
```

## Features

- **Atomic output** - lines never interleave, even across threads.
- **Context included automatically** - thread name, filename, line number, function name.
- **Defensive formatting** - repr-style output; broken `__repr__` and `__str__` never crash the call.
- **Drop-in parameters** - `sep`, `end`, `file` behave like `print()`.

## API

```python
printtrace(*values, sep=" ", end="\n", file=None, mode=None)
```

The `Mode` type alias is exported for use in annotations.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*values` | `object` | - | Values to print |
| `sep` | `str \| None` | `" "` | Separator (`None` → `" "`) |
| `end` | `str \| None` | `"\n"` | Terminator (`None` → `"\n"`) |
| `file` | `TextIO \| None` | `sys.stdout` | Output stream |
| `mode` | `str \| None` | env var / `"verbose"` | Output mode |

### Raises

`ValueError` - if `mode` (or `PRINTTRACE_MODE`) is not a valid mode.

## Modes

| Mode | Output | Formatting |
|------|--------|------------|
| `verbose` (default) | `[Thread] file:line in func \| values` | repr-style |
| `minimal` | values only | `str()` |
| `json` | `{"message": "...", "context": "..."}` | repr-style |

Set a process-wide default:

```bash
PRINTTRACE_MODE=minimal python myapp.py
```

The variable is read at call time, not import time.

An invalid mode raises immediately:

```python
printtrace("x", mode="vervose")  # ValueError: Invalid printtrace mode 'vervose'. ...
```

## Threaded debugging

```python
import threading
from printtrace import printtrace

def worker(i):
    printtrace("worker started", i)

for i in range(5):
    threading.Thread(target=worker, args=(i,)).start()
```

## Testing

```python
def test_output(capture_output):
    writer, get_lines = capture_output
    printtrace("hello", file=writer, mode="minimal")
    assert get_lines() == ["hello"]
```

The `capture_output` fixture lives in `tests/conftest.py`.

### Testing with environment variables

```python
def test_env_mode(monkeypatch):
    monkeypatch.setenv("PRINTTRACE_MODE", "minimal")
    buf = io.StringIO()
    printtrace("x", file=buf)
    assert " | " not in buf.getvalue()
```

## Writing a wrapper

```python
from printtrace.context import capture_context, _SKIP_FRAMES

def my_debug(*values, **kwargs):
    # +1 for the extra frame introduced by my_debug
    ctx = capture_context(skip=_SKIP_FRAMES + 1)
    ...
```

Each additional frame between user code and `capture_context` requires one more skip.

## When to use

- debugging multithreaded code
- CLI tools and scripts
- early development
- replacing temporary `print` statements

## When not to use

- structured logging pipelines
- long-running production log ingestion
- high-volume throughput (the global lock serialises all calls)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
