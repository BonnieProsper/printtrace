# Changelog

## [1.1.0] 16/03/2026

### Added

- `printtrace()` with `verbose`, `minimal`, and `json` output modes.
- Thread-safe output via a single global lock; formatting runs before the lock is acquired.
- `flush()` called outside the lock so a slow stream does not stall other threads.
- Call-site context: thread name, filename (basename), line number, function name.
- Repr-style value formatting with depth, item-count, and string-length caps.
- `PRINTTRACE_MODE` environment variable, read at call time.
- `Mode` type alias, `__version__`, `py.typed` marker (PEP 561).
- `pyproject.toml` with `[tool.mypy]` (strict) and `[tool.ruff]` configuration.

### Fixed

- **Mode validation**: invalid `mode` values, including `""`, now raise `ValueError`. Previously a typo silently fell through via falsy `or`-chaining.
- **`sep=None` / `end=None`**: normalised to `" "` and `"\n"` to match `print()`.
- **`minimal` mode safety**: `str()` now falls back to `repr()` then `"<unprintable>"` instead of propagating a broken `__str__` exception.
- **Namedtuple class name**: `format_value(Point(1, 2))` now renders as `Point(x=1, y=2)` instead of `(1, 2)`. Using `type(v) is tuple` instead of `isinstance` lets subclasses reach `repr()`.
- **List subclass `repr`**: same `type(v) is list` fix.
- **Empty `set()`**: was `"{}"`, indistinguishable from an empty dict. Now `"set()"`.
- **Empty `frozenset()`**: was `"frozenset({})"`. Now `"frozenset()"`.
- **Single-element tuples**: `(42,)` now includes the required trailing comma.
- **Non-empty frozensets**: now rendered as `frozenset({1, 2})` not `{1, 2}`.
- **Filename shortening**: uses `os.path.basename()` instead of a hardcoded `/` split.
- **`capture_context` skip exhaustion**: overshooting the stack now returns `CallContext(filename="<unknown>", ...)` instead of the last reachable frame.
- **Negative `skip`**: explicitly clamped to `0`.
- **Concurrent test fixture**: `test_multiline_under_concurrent_writes` now uses the thread-safe `capture_output` fixture instead of a bare `io.StringIO`.
