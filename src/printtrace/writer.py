from __future__ import annotations
from typing import TextIO

from .sync import output_lock


def write(file: TextIO, payload: str) -> None:
    with output_lock():
        file.write(payload)
