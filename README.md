# printtrace

A tiny, zero-configuration debugging primitive for Python.

`printtrace` is a deliberate middle ground between `print()` and `logging`:
- thread-safe
- ordered
- contextual
- no setup
- no global configuration
- no background threads

## Why not logging?

Logging is powerful, but heavy:
- handlers
- formatters
- configuration
- global state
- surprising defaults

`printtrace` is for moments when you just want reliable, readable debug output even under concurrency.

## Usage

```python
from printtrace import printtrace

printtrace("hello", {"a": 1})
```
Example output:
```csharp
[MainThread] app.py:42 in handler | 'hello' {'a': 1}
```
## Features

- Atomic output
  Lines never interleave, even across threads.
- Context included automatically
  - thread name
  - filename
  - line number
  - function name
- Defensive formatting
  Values are rendered using repr-style formatting for safer debugging output.
- Drop-in friendly
  Parameters mirror print() where it makes sense.

## API
```python
printtrace(*values, sep=" ", end="\n", file=None)
```

This is the only public API.

## Modes

- verbose (default): contextual, repr-style output
- minimal: print-compatible output
- json: structured output (experimental)

You can also set a default mode:
```bash
PRINTTRACE_MODE=minimal
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

printtrace is designed to be easy to test.
```python
def test_output(capture_output):
    writer, get_lines = capture_output
    printtrace("hello", file=writer, mode="minimal")
    assert get_lines() == ["hello"]
```

## When to use

- debugging multithreaded code
- CLI tools
- scripts
- early development
- replacing temporary print statements

## When not to use

- structured logging pipelines
- long-running production logging
- high-volume log ingestion systems

## License 

MIT