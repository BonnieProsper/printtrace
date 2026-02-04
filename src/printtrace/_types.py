from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class CallContext:
    filename: str
    lineno: int
    function: str
    thread_name: str
