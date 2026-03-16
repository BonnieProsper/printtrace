# Contributing to printtrace

## Philosophy

printtrace is deliberately small. Before adding a feature, ask whether it
pushes the library closer to `logging` (which already exists). If it does,
the answer is no.

## Setup

```bash
git clone <repo-url>
cd printtrace
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
```

The test suite includes concurrency tests with tight timing assertions.
If you see flaky failures, re-run once before investigating -  they are
occasionally affected by system load.

## Adding a wrapper around `printtrace`

If you write a helper that calls `printtrace()` internally, pass the
correct `skip` offset to `capture_context` so the reported call-site
points at your *caller*:

```python
from printtrace.context import capture_context, _SKIP_FRAMES

def my_debug(*values, **kwargs):
    # +1 for the extra frame introduced by my_debug
    ctx = capture_context(skip=_SKIP_FRAMES + 1)
    ...
```

Each additional frame between the caller and `capture_context` requires one more skip.

## Code style

This project uses `ruff` for linting and `mypy --strict` for type checking:

```bash
ruff check src tests
mypy src/printtrace
```

## Design constraints (do not violate)

These are documented in the source and are non-negotiable:

- **One global lock.** No queues, no worker threads, no async.
- **Lock scope is the write only.** Stack inspection and formatting happen
  before the lock is acquired.
- **No dependencies.** The package installs nothing beyond the stdlib.
- **format_value never raises.** All exception paths must be caught.
