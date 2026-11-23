"""JSON file storage for task records.

This module owns every byte of file I/O for taskcli: reading and validating
the envelope, atomic whole-file writes, the single-writer lock, and the
``add`` / ``done`` / ``delete`` mutations. It knows nothing about argparse
and never prints or exits; failures are reported through ``StorageError``
and ``TaskNotFoundError``.
"""
from __future__ import annotations

import dataclasses
import json
import os
import tempfile
import time
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from taskcli import models
from taskcli.models import STORAGE_VERSION, Task

_LOCK_RETRY_SECONDS: float = 0.025
_LOCK_TIMEOUT_SECONDS: float = 5.0
_LOCK_STALE_SECONDS: float = 60.0
_ENVELOPE_KEYS: frozenset[str] = frozenset({"version", "tasks"})


class StorageError(Exception):
    """Any file-level or schema-level failure while touching storage."""


class TaskNotFoundError(Exception):
    """The requested task id does not exist in the storage file."""


def default_path() -> Path:
    """Return the default storage path: ``taskcli.json`` in the cwd."""
    return Path.cwd() / "taskcli.json"


def _utc_now() -> str:
    """Return the current UTC time as ``YYYY-MM-DDTHH:MM:SSZ``."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _envelope(tasks: Sequence[Task]) -> dict[str, object]:
    """Build the on-disk envelope dict: exactly ``version`` and ``tasks``."""
    return {
        "version": STORAGE_VERSION,
        "tasks": [models.task_to_dict(task) for task in tasks],
    }


def _read_error(path: Path, detail: object) -> StorageError:
    return StorageError(f"cannot read storage file {path}: {detail}")


def _write_error(path: Path, detail: object) -> StorageError:
    return StorageError(f"cannot write storage file {path}: {detail}")


def read_tasks(path: Path) -> list[Task]:
    """Read and validate every task, in on-disk order.

    A missing file is an empty store: ``[]`` is returned and nothing is
    created on disk.
    """
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return []
    except OSError as exc:
        raise _read_error(path, exc) from exc

    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise _read_error(path, exc) from exc

    try:
        envelope = json.loads(text)
    except json.JSONDecodeError as exc:
        raise _read_error(path, exc) from exc

    if not isinstance(envelope, dict):
        raise _read_error(path, "top level must be a JSON object")

    keys = set(envelope)
    missing = _ENVELOPE_KEYS - keys
    if missing:
        raise _read_error(
            path, "missing envelope key(s) " + ", ".join(sorted(missing))
        )
    unknown = keys - _ENVELOPE_KEYS
    if unknown:
        raise _read_error(
            path, "unknown envelope key(s) " + ", ".join(sorted(unknown))
        )

    version = envelope["version"]
    if isinstance(version, bool) or not isinstance(version, int):
        raise _read_error(path, "version must be an integer")
    if version != STORAGE_VERSION:
        raise _read_error(
            path,
            f"unsupported storage version {version}, expected {STORAGE_VERSION}",
        )

    tasks = envelope["tasks"]
    if not isinstance(tasks, list):
        raise _read_error(path, "tasks must be a list")

    parsed: list[Task] = []
    for entry in tasks:
        try:
            parsed.append(models.task_from_dict(entry))
        except models.TaskDataError as exc:
            raise _read_error(path, exc) from exc
    return parsed


def _atomic_write(path: Path, obj: object) -> None:
    """Write ``obj`` to ``path`` atomically via a same-directory temp file."""
    directory = path.parent
    if not directory.is_dir():
        raise _write_error(path, f"directory {directory} does not exist")

    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(directory)
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(obj, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    except OSError as exc:
        raise _write_error(path, exc) from exc
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def write_tasks(path: Path, tasks: Sequence[Task]) -> None:
    """Atomically write the whole store, replacing the file entirely."""
    _atomic_write(path, _envelope(tasks))


def _lock_is_stale(lock_path: Path) -> bool:
    try:
        age = time.time() - lock_path.stat().st_mtime
    except OSError:
        return False
    return age > _LOCK_STALE_SECONDS


def _require_parent(path: Path) -> None:
    """Fail early with the write-time diagnostic for a missing parent."""
    directory = path.parent
    if not directory.is_dir():
        raise _write_error(path, f"directory {directory} does not exist")


@contextmanager
def _locked(path: Path) -> Iterator[None]:
    """Hold the single-writer lock for the duration of the block."""
    lock_path = Path(f"{path}.lock")
    deadline = time.monotonic() + _LOCK_TIMEOUT_SECONDS
    broke_stale = False
    fd: int | None = None
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if not broke_stale and _lock_is_stale(lock_path):
                broke_stale = True
                try:
                    os.unlink(lock_path)
                except OSError:
                    pass
                continue
            if time.monotonic() >= deadline:
                raise StorageError(
                    f"storage file is locked by another task process: {lock_path}"
                )
            time.sleep(_LOCK_RETRY_SECONDS)
        except OSError as exc:
            raise StorageError(f"cannot lock storage file {path}: {exc}") from exc
    try:
        yield
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        try:
            os.unlink(lock_path)
        except OSError:
            pass


def add_task(path: Path, title: str) -> Task:
    """Append a new pending task and return it."""
    _require_parent(path)
    with _locked(path):
        tasks = read_tasks(path)
        next_id = max((task.id for task in tasks), default=0) + 1
        created = models.new_task(next_id, title, _utc_now())
        write_tasks(path, [*tasks, created])
        return created


def set_done(path: Path, task_id: int, done: bool) -> Task:
    """Set the done flag of an existing task and return the updated task."""
    _require_parent(path)
    with _locked(path):
        tasks = read_tasks(path)
        for index, task in enumerate(tasks):
            if task.id == task_id:
                updated = dataclasses.replace(task, done=done)
                tasks[index] = updated
                write_tasks(path, tasks)
                return updated
        raise TaskNotFoundError(f"task {task_id} not found")


def delete_task(path: Path, task_id: int) -> Task:
    """Remove an existing task and return the removed task."""
    _require_parent(path)
    with _locked(path):
        tasks = read_tasks(path)
        for index, task in enumerate(tasks):
            if task.id == task_id:
                del tasks[index]
                write_tasks(path, tasks)
                return task
        raise TaskNotFoundError(f"task {task_id} not found")
