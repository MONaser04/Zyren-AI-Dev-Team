"""Command-line interface for taskcli.

This module owns every user-facing string: argparse wiring, the subcommand
handlers, stdout output, stderr diagnostics, and exit codes. It performs no
file I/O itself — every read and write is delegated to ``taskcli.storage``.
"""
from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from taskcli import models, storage

DEFAULT_PROG: str = "task"

_TITLE_ERROR: str = (
    "title must be 1-500 characters and must not contain "
    "newlines, tabs, or control characters"
)
_ID_ERROR: str = "task id must be a positive integer"


def _has_control_characters(text: str) -> bool:
    """Return True if text contains a C0 or C1 control character."""
    for char in text:
        code = ord(char)
        if code < 0x20 or 0x7F <= code <= 0x9F:
            return True
    return False


def _error(command: str, message: str) -> int:
    """Print a one-line domain error to stderr and return exit code 1."""
    print(f"{DEFAULT_PROG} {command}: error: {message}", file=sys.stderr)
    return 1


def cmd_add(args: argparse.Namespace, path: Path) -> int:
    """Add a new task with the given title."""
    title = args.title.strip()
    if not title or len(title) > models.MAX_TITLE_LEN or _has_control_characters(title):
        return _error("add", _TITLE_ERROR)
    task = storage.add_task(path, title)
    print(f"Added task {task.id}: {task.title}")
    return 0


def cmd_list(args: argparse.Namespace, path: Path) -> int:
    """List every task, sorted by id ascending."""
    tasks = storage.read_tasks(path)
    if not tasks:
        print("No tasks yet.")
        return 0
    for task in sorted(tasks, key=lambda item: item.id):
        marker = "[x]" if task.done else "[ ]"
        print(f"{task.id:>4}  {marker}  {task.title}  {task.created_at}")
    return 0


def cmd_done(args: argparse.Namespace, path: Path) -> int:
    """Mark a task as done by id."""
    if args.task_id <= 0:
        return _error("done", _ID_ERROR)
    task = storage.set_done(path, args.task_id, True)
    print(f"Task {task.id} marked done.")
    return 0


def cmd_delete(args: argparse.Namespace, path: Path) -> int:
    """Delete a task by id."""
    if args.task_id <= 0:
        return _error("delete", _ID_ERROR)
    task = storage.delete_task(path, args.task_id)
    print(f"Deleted task {task.id}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the root parser and its four subcommands."""
    parser = argparse.ArgumentParser(
        prog=DEFAULT_PROG,
        description="A small command-line task manager backed by a single JSON file.",
    )
    parser.add_argument(
        "--file",
        metavar="PATH",
        dest="storage_file",
        default=None,
        help="alternate storage file; must be given before the subcommand",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task.")
    add_parser.add_argument("title", metavar="TITLE", type=str, help="title of the new task")
    add_parser.set_defaults(handler=cmd_add)

    list_parser = subparsers.add_parser("list", help="List all tasks.")
    list_parser.set_defaults(handler=cmd_list)

    done_parser = subparsers.add_parser("done", help="Mark a task as done.")
    done_parser.add_argument(
        "task_id", metavar="ID", type=int, help="id of the task to mark done"
    )
    done_parser.set_defaults(handler=cmd_done)

    delete_parser = subparsers.add_parser("delete", help="Delete a task.")
    delete_parser.add_argument(
        "task_id", metavar="ID", type=int, help="id of the task to delete"
    )
    delete_parser.set_defaults(handler=cmd_delete)

    return parser


def run(args: argparse.Namespace) -> int:
    """Resolve the storage path and dispatch to the selected handler."""
    supplied = args.storage_file
    path = Path(supplied) if supplied else storage.default_path()
    try:
        return args.handler(args, path)
    except (storage.StorageError, storage.TaskNotFoundError, models.TaskDataError) as exc:
        return _error(args.command, str(exc))


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments and run the requested subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)
