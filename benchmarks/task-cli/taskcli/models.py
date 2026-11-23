"""Task record schema and JSON-dict conversion for taskcli.

This module owns the task data model and its validation rules. It knows
nothing about files, argparse, or user-facing text: it only converts between
``Task`` records and plain JSON-compatible dicts, and raises
``TaskDataError`` on any schema violation.
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

STORAGE_VERSION: int = 1
TASK_FIELDS: tuple[str, ...] = ("id", "title", "done", "created_at")
MAX_TITLE_LEN: int = 500

_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class TaskDataError(ValueError):
    """Raised when a task record violates the on-disk schema."""


@dataclass(frozen=True)
class Task:
    """A single task record: a dumb, immutable, unvalidated value object."""

    id: int
    title: str
    done: bool = False
    created_at: str = ""


def _control_characters(text: str) -> bool:
    """Return True if text contains a C0 or C1 control character."""
    for char in text:
        code = ord(char)
        if code < 0x20 or 0x7F <= code <= 0x9F:
            return True
    return False


def _validate_title_value(title: str) -> None:
    """Validate the stored form of a title: non-empty, bounded, no controls."""
    if not title or len(title) > MAX_TITLE_LEN or _control_characters(title):
        raise TaskDataError(
            "field 'title' must be 1-500 characters and must not contain "
            "newlines, tabs, or control characters"
        )


def _validate_title(title: str) -> str:
    """Validate a title and return the value to store (the stripped title)."""
    stored = title.strip()
    _validate_title_value(stored)
    return stored


def _validate_timestamp(created_at: str) -> None:
    if not _TIMESTAMP_RE.match(created_at):
        raise TaskDataError(
            "created_at must match YYYY-MM-DDTHH:MM:SSZ exactly"
        )


def new_task(task_id: int, title: str, created_at: str) -> Task:
    """Build a validated pending ``Task`` from raw constructor arguments."""
    stored_title = _validate_title(title)
    _validate_timestamp(created_at)
    return Task(id=task_id, title=stored_title, done=False, created_at=created_at)


def task_from_dict(data: Mapping[str, object]) -> Task:
    """Validate a plain JSON object and convert it into a ``Task``."""
    keys = set(data)
    expected = set(TASK_FIELDS)
    for name in TASK_FIELDS:
        if name not in keys:
            raise TaskDataError(f"missing required field '{name}'")
    for name in sorted(keys - expected):
        raise TaskDataError(f"unknown field '{name}'")

    task_id = data["id"]
    if isinstance(task_id, bool) or not isinstance(task_id, int):
        raise TaskDataError("field 'id' must be an integer")
    if task_id < 1:
        raise TaskDataError("field 'id' must be a positive integer")

    title = data["title"]
    if not isinstance(title, str):
        raise TaskDataError("field 'title' must be a string")
    _validate_title_value(title)

    done = data["done"]
    if not isinstance(done, bool):
        raise TaskDataError("field 'done' must be a boolean")

    created_at = data["created_at"]
    if not isinstance(created_at, str):
        raise TaskDataError("field 'created_at' must be a string")
    _validate_timestamp(created_at)

    return Task(id=task_id, title=title, done=done, created_at=created_at)


def task_to_dict(task: Task) -> dict[str, object]:
    """Return a new plain dict with the four task keys in canonical order."""
    return {
        "id": task.id,
        "title": task.title,
        "done": task.done,
        "created_at": task.created_at,
    }
