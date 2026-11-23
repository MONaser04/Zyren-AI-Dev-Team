# task-cli

A small, single-file-backed command-line task manager written in Python. Four
subcommands — `add`, `list`, `done`, `delete` — over a task list persisted as
one UTF-8 JSON document on disk.

`task-cli` is stdout/stderr text and exit codes only: no editing, no colors,
no configuration file, no network, no database.

## Storage

Tasks are stored in a single JSON file with the shape:

```json
{
  "version": 1,
  "tasks": [
    {
      "id": 1,
      "title": "Buy milk",
      "done": false,
      "created_at": "2026-11-11T09:30:00Z"
    }
  ]
}
```

## Install

```powershell
pip install .
```

This installs a console script named `task`:

```powershell
task --help
```

## Zero-install usage

Thanks to the flat package layout, the package runs with no install step from
the project root (the directory containing `pyproject.toml`):

```powershell
python -m taskcli --help
```

Both invocation forms — `task <subcommand>` and `python -m taskcli <subcommand>`
— produce byte-identical stdout, stderr, and exit codes, because the program
name is pinned in the parser (`prog="task"`).

## Commands

### `add` — add a new task

```powershell
task add "Buy milk"                    # Added task 1: Buy milk
python -m taskcli add "Write design doc"   # Added task 2: Write design doc
```

### `list` — list all tasks

```powershell
task list
```

```text
   1  [ ]  Buy milk  2026-11-11T09:30:00Z
   2  [x]  Write the design doc  2026-11-10T08:00:00Z
```

Tasks are printed sorted by id ascending. `[x]` means done, `[ ]` means
pending. An empty store prints exactly `No tasks yet.`

### `done` — mark a task done

```powershell
task done 2                 # Task 2 marked done.
```

`done` is one-way and idempotent: marking an already-done task succeeds and
prints the same line.

### `delete` — delete a task

```powershell
task delete 2               # Deleted task 2.
```

Ids are allocated as `max(existing ids) + 1`. If the deleted task held the
highest id, the next `add` reuses that id; otherwise a strictly higher id is
allocated. Surviving tasks are never renumbered or reordered by a delete.

## The `--file` option

`--file PATH` selects an alternate storage file. It is a **root-parser
option**, so it must appear **before** the subcommand:

```powershell
task --file C:\tmp\mytasks.json add "Buy milk"
task --file C:\tmp\mytasks.json list
```

Placed after the subcommand it is *not* recognized:

```powershell
task add "x" --file C:\tmp\mytasks.json
# task: error: unrecognized arguments: --file C:\tmp\mytasks.json   (exit 2)
```

No subcommand defines a second `--file`; there is exactly one storage-path
option, on the root parser.

## Default storage path

Without `--file`, the storage file is `taskcli.json` in the **current working
directory**. Reading a missing file is not an error: it is treated as an empty
store (`No tasks yet.`) and nothing is created on disk — the file is created
only by a mutating command (`add`, `done`, `delete`).

## Exit codes

| Code | Meaning | Source |
| --- | --- | --- |
| 0 | Success | returned by the subcommand handler |
| 1 | Domain error: empty/too-long/control-character title, non-positive id, unknown task id, unreadable or corrupt storage file, unwritable storage file, storage file locked | caught in `cli.run`, printed as `task {command}: error: {message}` on stderr |
| 2 | Usage error: unknown subcommand, missing or extra argument, non-integer `ID`, misplaced `--file` | argparse |

Domain errors print a single stderr line with no traceback, for example:

```text
task done: error: task 99 not found
```

## Design

The normative, approved contract for this package — data schema, command
contracts, atomic-write and locking behavior, module boundaries — is
[`DESIGN.md`](DESIGN.md).
