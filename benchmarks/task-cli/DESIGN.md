# DESIGN — `task-cli`

Status: **PENDING APPROVAL**. No code, `pyproject.toml`, or `README.md` may be written until this document is approved.
Author: zyren-planner. Date: 2026-11-11.

---

## 1. Overview

`task-cli` is a small, single-file-backed command-line task manager written in Python. It provides four subcommands — `add`, `list`, `done`, `delete` — over a task list persisted as one UTF-8 JSON document on disk. The implementation is a proper Python package with three strictly separated concerns: a data-model module that owns the task schema, a storage module that owns the JSON file and atomic persistence, and a CLI module that owns argparse wiring and user-facing I/O. The whole program is stdout/stderr text and exit codes only: no editing, no colors, no configuration file, no network, no database.

**Scope.** Four subcommands; one JSON storage file; positive-integer task ids allocated as `max(existing ids) + 1`, which means an id **may be reused** once the task holding it is deleted (§3.4, §5.2); deterministic, line-oriented `list` output suitable for piping; exit codes 0 / 1 / 2; a global `--file` option to relocate the storage file.

**Non-goals (explicitly out of scope, must not be implemented):**

- No editing or renaming of existing task titles.
- No priorities, tags, projects, due dates, reminders, or recurrence.
- No sub-tasks, notes, or attachments.
- No un-done / toggle (`done` is one-way and idempotent).
- No persistence beyond the single JSON file — no SQLite, no config file, no environment-variable overrides other than the one documented in §4, no multiple files.
- No interactive prompts, no TUI, no pagers, no ANSI color, no Unicode symbols beyond plain ASCII.
- No concurrency features beyond the single-writer file lock in §5; no multi-user or networked access.
- No plugin system, no shell completion scripts, no man pages.
- No test suite files (verification is performed by the deterministic shell commands in §7).

---

## 2. File layout

Absolute root: `<repo-root>/benchmarks/task-cli`

Every file below is created by the coder. This is the complete, closed list — no additional files.

```
<repo-root>/benchmarks/task-cli/
├── DESIGN.md                                  # This document: approved contract for the whole build.
├── README.md                                  # Human-facing usage, install, and exit-code reference.
├── pyproject.toml                             # Package metadata, build backend, [project.scripts] entry point.
├── .gitignore                                 # Ignores the JSON data file, lock files, and Python build artifacts.
├── taskcli\
│   ├── __init__.py                            # Package marker: one-line docstring + __version__ only; no imports of siblings.
│   ├── __main__.py                            # Enables `python -m taskcli`; two lines, no __name__ fence.
│   ├── models.py                              # Task record + JSON-dict conversion + schema constants. Knows nothing about files.
│   ├── storage.py                              # JSON read/write, atomic replace, file lock, CRUD. Knows nothing about argparse.
│   └── cli.py                                 # argparse wiring, subcommand handlers, stdout/stderr text, exit codes.
└── taskcli.json                               # NOT committed — created at runtime by the program (ignored by .gitignore).
```

### 2.1 Layout choice: **flat** (no `src/` directory)

The package directory `taskcli` sits directly beside `pyproject.toml`.

**Justification.** The PyPA command-line-tools guide documents the exact trade-off: with a flat layout `python -m greetings` "works immediately with flat layout, but requires installation of the package with src layout" (<https://packaging.python.org/en/latest/guides/creating-command-line-tools/>). The human's requirement is that `python -m <package>` must work with **zero installation steps**, and the verification plan in §7 runs the program by module invocation from the project root. A `src/` layout would make those commands fail with `ModuleNotFoundError` until an editable or regular install was performed, adding an install prerequisite the human did not ask for. Flat layout is therefore mandatory.

**Consequence the coder must honor.** With a flat layout there must be **no `sys.path` manipulation anywhere in any module**, and no top-level module named `taskcli.py`, `json.py`, `argparse.py`, `dataclasses.py`, `tempfile.py`, `os.py`, or `typing.py` that could shadow the stdlib. The only importable top-level name is the `taskcli` package.

**The trade-off this layout buys (normative).** Flat layout trades "importable from anywhere" for "importable with zero installation": `python -m taskcli` resolves only when the project root is on `sys.path`, i.e. when the current working directory is `<repo-root>/benchmarks/task-cli` (or the package has been installed). Running `python -m taskcli` from any other directory therefore fails with `No module named taskcli` — this is expected behavior, not a defect, and §7 V32a/V32b pin it. `pip install .` from the project root (documented in `README.md`, §2.2) is the supported way to get a `task` command on `PATH` that works from any directory.

### 2.1.1 Required `.gitignore` contents (described, not written by this document)

Exactly these entries: `taskcli.json`, `*.lock`, `__pycache__/`, `*.py[cod]`, `*.egg-info/`, `build/`, `dist/`, `.venv/`, `venv/`.

### 2.2 `README.md` required sections (described, not written by this document)

Purpose; install (`pip install .`); the four commands with one example each; the `--file` option and its **required position before the subcommand**; exit-code table (0/1/2); the default storage path; a link back to `DESIGN.md`.

---

## 3. Data model contract

### 3.1 On-disk JSON schema

The storage file is a single UTF-8 JSON **object** (an envelope), not a bare array:

```json
{
  "version": 1,
  "tasks": [
    {
      "id": 1,
      "title": "Buy milk",
      "done": false,
      "created_at": "2026-11-11T09:30:00Z"
    },
    {
      "id": 2,
      "title": "Write the design doc",
      "done": true,
      "created_at": "2026-11-10T08:00:00Z"
    }
  ]
}
```

| Element | Type | Notes |
| --- | --- | --- |
| top-level | object | Exactly two keys: `version`, `tasks`. No other keys are permitted. |
| `version` | int | Always `1` (`models.STORAGE_VERSION`). Any other value is a corrupt-file error (§3.6). |
| `tasks` | array of task objects | May be empty. Order on disk is the order in which tasks were written; the `list` command re-sorts by `id` for display, so on-disk order is not part of the user-visible contract. |

**Task object fields — exact names, exact types, exact order of keys in the JSON text:**

| # | Field | JSON type | Python type | Required | Default | Constraint |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | number (integer) | `int` | yes | — | `>= 1`. Booleans are **not** valid ids (`isinstance(True, int)` is `True` in Python, so a `bool` must be explicitly rejected). |
| 2 | `title` | string | `str` | yes | — | `1 <= len(title) <= 500`; no `\n`, `\r`, `\t`, or any C0/C1 control character. |
| 3 | `done` | boolean | `bool` | yes | `false` | Must be a real JSON boolean; `0`/`1` and `"true"` are rejected. |
| 4 | `created_at` | string | `str` | yes | — | Must match `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$` exactly (UTC, second precision, literal `Z`, no fractional seconds, no offset). |

A task object with a missing key, an extra/unknown key, or a wrong-typed value is a **corrupt file** error (exit 1), not a silently-repaired record.

### 3.2 Timestamp format

`created_at` is UTC ISO-8601 with second precision and a literal `Z` suffix: `YYYY-MM-DDTHH:MM:SSZ`. It is generated once at `add` time and is **immutable** — `done` and `delete` never touch it. Sub-second precision is truncated (not rounded) away. Validation is by regular expression only; `models` does **not** import `datetime` and does not round-trip through `datetime.fromisoformat`, so a value like `2026-02-30T00:00:00Z` is accepted as a well-formed *string* even though it is not a real calendar date. This is a deliberate, documented simplification.

### 3.3 `done` flag representation

A real JSON boolean, `false` for pending and `true` for complete. Never an integer, never a string, never `null`. The key name is `done` (not `completed`, not `is_done`).

### 3.4 ID allocation

`max(existing ids) + 1`; `1` when the store is empty. There is **no** stored counter and no `next_id` field in the envelope. Rationale: a counter can silently desynchronize from the actual ids (hand-edited file, interrupted write, restore from backup) and then either reuse an id or collide; `max + 1` cannot desynchronize because it is derived from the only authoritative data, the id set itself. That same derivation is what makes the surviving id set the *only* authoritative record of what has been allocated, and it carries a direct, normative consequence: **ids are not permanently retired — if the deleted task held the maximum id, the next `add` reuses that id**, because the surviving set no longer contains it. What `delete` never does is renumber surviving tasks or reorder records, so any surviving id is stable for as long as its task exists. §5.2 states the identical rule from the `delete` side and §7 V20b pins it deterministically.

### 3.5 `Task` class contract (`taskcli/models.py`)

`Task` is a **frozen dataclass** and a dumb record: it performs **no validation** (no `__post_init__`), raises nothing, and exposes exactly these fields in this order:

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `id` | `int` | — | no default |
| `title` | `str` | — | no default |
| `done` | `bool` | `False` | the only meaningful default |
| `created_at` | `str` | `""` | default exists only to satisfy dataclass field ordering |

Decorators required: `@dataclass(frozen=True)`. Frozen because a `Task` handed to `cli` must not be mutable by accident; mutation happens by constructing a new `Task` via `dataclasses.replace`.

**Field-order rationale (normative).** In a dataclass a non-default field cannot follow a defaulted one — `Task` with `done` defaulted and `created_at` undefaulted raises `TypeError: non-default argument 'created_at' follows default argument 'done'` at import time. `created_at` therefore carries the empty-string default. That default is an ordering artifact and is **never observed in stored data**: both sanctioned constructors (`new_task`, `task_from_dict`) pass `created_at` explicitly, `new_task` rejects the empty string against the §3.2 regex, and `task_from_dict` requires the key to be present and well-formed, so a `Task` with `created_at == ""` cannot be produced by any sanctioned path and cannot be serialized by `task_to_dict` into a valid record.

**Construction rule (no ambiguity):** the only two sanctioned constructors are `new_task(...)` and `task_from_dict(...)`. Direct `Task(...)` calls from `cli.py` or `storage.py` are forbidden by this contract; they would bypass validation.

**`Task` is not JSON-serializable.** `json.dump` will raise `TypeError` on a `Task`. Every conversion to a plain dict must go through `task_to_dict`. This is the reason `models` owns the dict conversion rather than `storage` doing it inline.

### 3.6 Dict ↔ `Task` conversion, and the `object_hook` decision

`json.load` returns plain `dict` / `list` / `str` / `int` / `bool` / `None` objects — never `Task` instances. An explicit conversion step is therefore unavoidable. The question is *where*.

**Decision: `object_hook` and `object_pairs_hook` are NOT used, anywhere, in this project.**

Justification, from the documented semantics of `json.load`:

- `object_hook` is invoked for **every** JSON object decoded in the whole document, not just the ones you care about. A single hook function would be called once for the envelope `{"version":…, "tasks":[…]}` and once for each task object, with no reliable way to tell them apart other than sniffing the keys — and a task object that happens to be missing a key would be indistinguishable from the envelope. Using `object_hook` therefore forces key-sniffing heuristics inside a hook that cannot raise a clean, typed error.
- `object_pairs_hook` has the same document-wide firing problem, and additionally bypasses the duplicate-key detection that plain `dict` construction gives you.
- Post-processing at a single, explicit boundary keeps the failure mode obvious: `storage` decodes the envelope, walks `tasks`, and calls `models.task_from_dict` once per element. Errors surface as `models.TaskDataError` with a precise field name, which is exactly what §4's error messages need.

The documented hook is acknowledged and deliberately rejected on those grounds; the conversion is instead specified as follows.

```text
models.task_from_dict(data) -> Task
models.task_to_dict(task)  -> dict
```

- `task_to_dict(task: Task) -> dict[str, object]` — returns a **new** plain dict with exactly the four keys, inserted in the order `id, title, done, created_at`, values copied verbatim. The returned dict is what `storage` puts into the envelope for `json.dump`.
- `task_from_dict(data: Mapping[str, object]) -> Task` — validates the exact key set (`set(data) == {"id","title","done","created_at"}`), validates each value against the §3.1 table, and returns `Task(...)`. Raises `TaskDataError` (a subclass of `ValueError`, so it is caught by any `except ValueError`) with a message naming the offending field.

**Key order on disk is insertion order, and `sort_keys` is NEVER passed to `json.dump`.** With `sort_keys=True` the envelope would serialize as `{"tasks": …, "version": 1}` (alphabetical), contradicting the schema above; specifying `indent` is the only documented way to add whitespace ("Newlines are only inserted via `indent`").

---

## 4. Command contracts

Program name (in all messages and `parser.prog`): **`task`**.
Invocation forms: `task <subcommand> …` (console script, §6.3) or `python -m taskcli <subcommand> …` (zero-install form). Both produce byte-identical stdout, stderr, and exit codes, because `build_parser()` pins `prog="task"` explicitly. This is essential: when run as `python -m taskcli`, `sys.argv[0]` is the path of `__main__.py`, and argparse would otherwise derive a prog of `__main__.py` and print a different usage prefix in the two modes.

### 4.0 Global options (root parser only)

| Flag | Metavar | Type | Required | Default | Dest | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `--file` | `PATH` | `str` (filesystem path) | no | `None` | **`storage_file`** | Alternate storage file. **Must appear before the subcommand**: `task --file C:\tmp\x.json add "y"`. Resolved as `args.storage_file or storage.default_path()`. `--file` is declared **only** on the root parser. |
| `-h`, `--help` | — | — | no | — | — | Auto-generated; exit 0. |

**Position is enforced by argparse, not by custom code.** Root-parser optionals are only recognized before the subcommand token, so `task add "y" --file x.json` fails with `unrecognized arguments: --file x.json` on stderr and **exit 2**. This is the documented argparse behavior and is accepted as-is; no subparser declares a second `--file` to work around it.

**Documented namespace gotcha and the distinct-dest rule.** The argparse documentation states: *"If a subparser defines an argument with the same dest as the parent parser, the two share a single namespace attribute, so the parent's value won't be retained. Users should give them distinct dest values"* (<https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers>). Accordingly:

- The root `--file` uses `dest="storage_file"` — **not** the argparse-derived dest `file`.
- **No subparser in this project defines `--file`.** The collision therefore cannot occur, and there is exactly one namespace attribute for the storage path.
- If a future subcommand genuinely needs its own path option, it **must** use a distinct dest — the mandated name here is `dest="subcommand_file"` — and must be spelled differently from `--file` on the command line as well. Distinct *spellings* with the *same* dest do **not** fix the problem: the sharing is keyed on dest, so `--file` on the root and `--data` on a subparser both defaulting to dest `file` would still collide. Resolution in that hypothetical future would be `args.subcommand_file or args.storage_file or storage.default_path()`, evaluated in that precedence order.

### 4.1 `add`

| | |
| --- | --- |
| Invocation | `task add TITLE` |
| Positional | `TITLE`, `metavar="TITLE"`, `type=str`, `nargs` unset (exactly one argument), **required** |
| Optionals | global `--file` only |
| Constraint | `1 <= len(title.strip())` … see below |

**Title validation (domain rules, checked in `cli`, not by argparse `type=`):**

1. `title.strip()` must be non-empty → a whitespace-only or empty title is rejected.
2. The **stored** title is the `strip()`-ed value (leading/trailing whitespace is removed; interior runs of spaces are preserved verbatim).
3. Must not contain `\n`, `\r`, `\t`, or any other C0/C1 control character — otherwise one task could emit multiple `list` lines.
4. `len(stored_title) <= 500`.

**Success stdout (exactly one line, trailing `\n`):**

```text
Added task {id}: {title}
```

e.g. `Added task 1: Buy milk`

**Side effect:** appends a `Task` with `done=False`, `id = max(ids)+1`, `created_at = now`, then writes the whole file atomically (§5).

**Errors:**

| Trigger | stderr | Exit |
| --- | --- | --- |
| `TITLE` missing / more than one positional | argparse usage + `the following arguments are required: TITLE` (or `unrecognized arguments`) | 2 |
| Empty/whitespace-only title, control character, or title longer than 500 chars | `task add: error: title must be 1-500 characters and must not contain newlines, tabs, or control characters` | 1 |
| Storage file unreadable/corrupt | `task add: error: cannot read storage file {path}: {detail}` | 1 |
| Storage file unwritable (permissions, missing parent directory, disk full) | `task add: error: cannot write storage file {path}: {detail}` | 1 |

### 4.2 `list`

| | |
| --- | --- |
| Invocation | `task list` |
| Positional | none — any positional argument is a usage error |
| Optionals | global `--file` only |

Tasks are printed **sorted by `id` ascending** (presentation sort in `cli`; `storage.read_tasks` returns on-disk order untouched). `list` performs a lock-free read.

**Per-task line format — exact template:**

```text
{id:>4}  {marker}  {title}  {created_at}
```

- `{id:>4}` — the id right-aligned in a field of width 4, space-padded (ids above 9999 simply widen; no truncation).
- Separator: **exactly two spaces**.
- `{marker}` — exactly `[x]` for a done task, exactly `[ ]` (open bracket, one space, close bracket) for a pending task.
- Separator: exactly two spaces.
- `{title}` — the stored title verbatim.
- Separator: exactly two spaces.
- `{created_at}` — the raw stored timestamp string.

**Exact successful output for the §3.1 example file:**

```text
   1  [ ]  Buy milk  2026-11-11T09:30:00Z
   2  [x]  Write the design doc  2026-11-10T08:00:00Z
```

**Empty-list output — the exact single line (trailing `\n`):**

```text
No tasks yet.
```

`No tasks yet.` is used in exactly two situations: the storage file does not exist, and the storage file exists with `"tasks": []`. No header, no trailing summary line, no counts, no summary footer.

**Errors:**

| Trigger | stderr | Exit |
| --- | --- | --- |
| Unexpected positional argument | argparse usage | 2 |
| File exists but is not valid JSON / wrong shape / bad task record | `task list: error: cannot read storage file {path}: {detail}` | 1 |
| Path exists but is a directory, or is unreadable | `task list: error: cannot read storage file {path}: {detail}` | 1 |

### 4.3 `done`

| | |
| --- | --- |
| Invocation | `task done ID` |
| Positional | `ID`, `metavar="ID"`, `type=int`, **required** |
| Optionals | global `--file` only |

**Success stdout (exactly one line):**

```text
Task {id} marked done.
```

e.g. `Task 1 marked done.`

**Idempotency:** marking an already-done task is a success, prints the same line, and rewrites the file unchanged in content (the write still happens, producing an identical file). `done` never clears the flag — there is no un-done command.

**Side effect:** sets `done = true` on the matching task, then writes the whole file atomically.

**Errors:**

| Trigger | stderr | Exit |
| --- | --- | --- |
| `ID` missing, or more than one positional | argparse usage | 2 |
| `ID` is not an integer (`abc`, `1.5`, `1e3`) | argparse usage: `argument ID: invalid int value: 'abc'` | 2 |
| `ID <= 0` | `task done: error: task id must be a positive integer` | 1 |
| No task with that id | `task done: error: task 99 not found` | 1 |
| Read/write failure as in §4.1 | `task done: error: cannot read storage file {path}: {detail}` / `… cannot write …` | 1 |

Note the deliberate split: *syntactically* invalid `ID` (argparse can reject it) → 2; *semantically* invalid or absent id → 1.

### 4.4 `delete`

| | |
| --- | --- |
| Invocation | `task delete ID` |
| Positional | `ID`, `metavar="ID"`, `type=int`, **required** |
| Optionals | global `--file` only |

**Success stdout (exactly one line):**

```text
Deleted task {id}.
```

e.g. `Deleted task 1.`

**Side effect:** removes the task from the array, then writes the whole file atomically. **Other ids are not renumbered and no other record is modified.** Because ids are `max + 1` (§3.4), the next `add` allocates `max(surviving ids) + 1` — which equals the deleted id when the deleted task held the maximum, and a strictly larger id otherwise. The deleted id is therefore **not** guaranteed to be retired; it is handed back out whenever it was the maximum (§5.2, pinned by §7 V20b).

**Errors:** identical table to §4.3, with the command name `task delete: error:` substituted, and the same 2-vs-1 split.

### 4.5 Exit-code summary (normative)

| Code | Meaning | Source |
| --- | --- | --- |
| 0 | Success | returned by handler |
| 1 | Domain error: unknown/invalid id, invalid title, unreadable or corrupt storage file, unwritable storage file | caught in `cli.run` |
| 2 | Usage error: unknown subcommand, missing/extra argument, non-integer `ID`, misplaced `--file`, `-h` misuse | argparse |
| 130 | KeyboardInterrupt — **not implemented**, listed only to record that no handler exists | — |

Basis for the 2/1 split: `parser.error()` "terminates the program with a status code of 2" (argparse docs), and `python -m` documents that "Unix programs generally use 2 for command line syntax errors and 1 for all other kinds of errors" (<https://docs.python.org/3/using/cmdline.html#cmdoption-m>).

### 4.6 stderr message format (normative)

Every domain error is a single line, no traceback, no `usage:` block:

```text
task {command}: error: {message}
```

`{command}` is the subcommand name captured in the namespace (`dest="command"` on `add_subparsers`). `{message}` never ends with a period. Where the message cites a path, `{path}` is the resolved path exactly as `--file` supplied it, or the default from `storage.default_path()`.

---

## 5. ID allocation and concurrency

### 5.1 Next id

`next_id = max(t.id for t in tasks) + 1` if any tasks exist, else `1`. Computed inside `storage.add_task`, while the lock is held, immediately after the read. There is no persisted counter and no `next_id` key in the envelope (rationale in §3.4).

**Why no high-water mark (normative ruling).** A persisted high-water mark would require a third envelope key, which the two-key envelope §3.1 forbids and §7 V6 asserts. The accepted trade-off is that an id may be reused after its task is deleted (§5.2). What the rule does preserve is the part that matters operationally: uniqueness within the live id set, no collisions, and no desynchronization between the allocated id and the file contents.

### 5.2 Delete and reuse

Deleting id `k` does not renumber surviving tasks, does not compact the array, and does not modify any other record: surviving tasks keep their ids, their relative order, their titles, their `done` flags, and their `created_at` values.

The deleted id is **not** permanently retired. Because `add` is `max(surviving ids) + 1`:

- If `k` was **not** the maximum, the maximum survives, so the next `add` returns `max + 1` — strictly greater than `k`, and `k` is not handed out at that point.
- If `k` **was** the maximum, the surviving maximum is lower, so the next `add` returns exactly `max(surviving) + 1`, which equals `k`. The deleted maximum id is handed straight back out.

This is structural, not an oversight: the surviving id set is the only authoritative record of what has been allocated, and a file that no longer mentions `k` cannot be distinguished from one in which `k` was never allocated. A high-water mark that would distinguish them needs a third envelope key, which the schema (§3.1) forbids; §5.1 records that ruling. Ids can additionally be reused if a user hand-edits the JSON file to lower or remove an id — that is out of contract. §7 V20b pins both branches deterministically.

### 5.3 Atomic write recipe and its status

Every mutation writes the **entire** file (the program never mutates in place). The recipe:

1. Acquire the lock (§5.4).
2. Create a temporary file **in the same directory as the target file** — required because `os.replace` "may fail if `src` and `dst` are on different filesystems" (<https://docs.python.org/3/library/os.html#os.replace>).
3. Write the envelope with `json.dump(envelope, fh, indent=2, ensure_ascii=False)`, then a single `"\n"`, then `fh.flush()` and `os.fsync(fh.fileno())`.
4. Close the temporary file, then `os.replace(tmp_path, target_path)`.
5. On any exception, `os.unlink` the temporary file in an `except`/`finally` block so no `.tmp` litter survives.
6. Release the lock.

**Status of this recipe: community practice, not official documentation.** `os.replace` itself is documented as an atomic rename on POSIX and is the documented Windows `MoveFileEx`-with-replace equivalent, but the *pattern* of temp-file-in-same-directory-plus-`os.replace` for crash-safe file updates appears nowhere in the Python standard-library docs. It is specified here because it is the standard practice and because it is strictly better than `open(path, "w")` truncation, which can leave a half-written file. No test in §7 depends on crash-atomicity being observable; the tests only depend on the resulting file being valid JSON.

**No official trailing-newline rule exists.** The single trailing `"\n"` after `json.dump` is a project convention (POSIX text-file friendliness, clean shell prompts), not a documented requirement.

### 5.4 Single-writer lock

Concurrency is limited to the realistic case of two invocations racing on one file.

- Lock file: `{target_path}.lock` — e.g. `C:\…\task-cli\taskcli.json.lock`. It is a side-effect artifact, must be removed in a `finally`, and is covered by the `*.lock` line of `.gitignore` (§2.1.1).
- Creation: `os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)`. `O_EXCL` is the portable, stdlib-only, correctness-checking primitive (no `fcntl`/`msvcrt`, so the same code works on the win32 target and POSIX).
- Contention: retry every 25 ms for up to 5 seconds, then fail with a domain error: `task {command}: error: storage file is locked by another task process: {lock_path}`, exit 1.
- Stale lock: if the lock file's modification time is older than 60 seconds, unlink it and retry once (best-effort recovery from a killed process). Two processes may still both break a stale lock; the resulting write is a last-writer-wins overwrite of the whole file, which is an accepted limitation of a single-writer CLI.
- Scope: the lock is held across the read-modify-write of `add_task`, `set_done`, and `delete_task`. `read_tasks` (used by `list`) does **not** lock — a lock-free read sees either the complete old file or the complete new file, which is precisely what the atomic replace buys.

---

## 6. Module contracts

Import graph (no cycles, one direction only):

```text
taskcli/__init__.py   → (nothing)
taskcli/__main__.py   → taskcli.cli
taskcli/cli.py        → taskcli.models, taskcli.storage, stdlib only
taskcli/storage.py    → taskcli.models, stdlib only
taskcli/models.py     → stdlib only
```

Enforcement rules:

- `models` imports nothing from the package. It must not import `storage`, `cli`, or `json` at module level for file work — it uses `json` nowhere at all.
- `storage` imports `models` only. It must **not** import `argparse`, must not import `cli`, must not print anything, and must not call `sys.exit`.
- `cli` imports both. It must not import `json` and must not call `open`/`os.replace`/`tempfile` — all file I/O is delegated to `storage`, per the separation the human required.
- No module manipulates `sys.path`.
- Every module begins with `from __future__ import annotations`, so PEP 585/604 annotations are safe under the declared `requires-python`.

### 6.1 `taskcli/__init__.py`

| Member | Kind | Contract |
| --- | --- | --- |
| `__version__` | `str` literal | `"0.1.0"`. Must match `version` in `pyproject.toml`; the coder updates both together (no dynamic-version machinery). |
| module docstring | — | One line: description of the package. |

No other names, no re-exports, no imports of sibling modules.

### 6.2 `taskcli/models.py` — data models (owns the schema, knows nothing about files)

| Member | Signature | Returns / Raises |
| --- | --- | --- |
| `STORAGE_VERSION` | `int = 1` | envelope version constant |
| `TASK_FIELDS` | `tuple[str, …] = ("id", "title", "done", "created_at")` | canonical field order used by both `task_from_dict` and `task_to_dict` |
| `MAX_TITLE_LEN` | `int = 500` | title length cap |
| `Task` | frozen dataclass, fields per §3.5 | no validation, no `__post_init__` |
| `TaskDataError` | `class TaskDataError(ValueError)` | raised on any schema violation |
| `new_task` | `(task_id: int, title: str, created_at: str) -> Task` | validates `title` (strip → non-empty, no control chars, `<= MAX_TITLE_LEN`), validates `created_at` against the regex, returns `Task(id=task_id, title=title, done=False, created_at=created_at)`. Raises `TaskDataError`. Note: the stored title is the stripped one. |
| `task_from_dict` | `(data: Mapping[str, object]) -> Task` | exact key-set and type validation per §3.1. Raises `TaskDataError` naming the field. |
| `task_to_dict` | `(task: Task) -> dict[str, object]` | new dict, keys inserted in `TASK_FIELDS` order, values verbatim. |

### 6.3 `taskcli/storage.py` — storage (owns the file; knows nothing about argparse)

| Member | Signature | Returns / Raises |
| --- | --- | --- |
| `StorageError` | `class StorageError(Exception)` | any file-level or schema-level failure |
| `TaskNotFoundError` | `class TaskNotFoundError(Exception)` | unknown task id |
| `default_path` | `() -> Path` | `Path.cwd() / "taskcli.json"` — the single documented default storage path |
| `read_tasks` | `(path: Path) -> list[Task]` | **missing file → `[]`** (no error, nothing created). Valid file → validated `Task` list in on-disk order. Raises `StorageError` on: not-JSON (including a 0-byte file), top-level not an object, missing/unknown envelope keys, `version != STORAGE_VERSION`, `tasks` not a list, or any `TaskDataError` from a record. |
| `write_tasks` | `(path: Path, tasks: Sequence[Task]) -> None` | atomic whole-file write per §5.3. Does not create missing parent directories; a missing parent raises `StorageError`. |
| `add_task` | `(path: Path, title: str) -> Task` | lock → read → `new_task(max+1, title, utc_now())` → append → write → unlock. Returns the created `Task`. |
| `set_done` | `(path: Path, task_id: int, done: bool) -> Task` | lock → read → locate → replace with `dataclasses.replace(task, done=done)` → write → unlock. Returns the updated `Task`. Raises `TaskNotFoundError` if absent. |
| `delete_task` | `(path: Path, task_id: int) -> Task` | lock → read → remove → write → unlock. Returns the removed `Task`. Raises `TaskNotFoundError` if absent. |

Module-private helpers permitted (not part of the public contract): `_locked(path)` context manager implementing §5.4, `_utc_now() -> str` producing the §3.2 string, `_envelope(tasks) -> dict`, `_atomic_write(path, obj)`. They stay inside `storage` — `cli` never touches them.

### 6.4 `taskcli/cli.py` — CLI parsing (owns argparse and all user-facing text; no direct file I/O)

| Member | Signature | Returns |
| --- | --- | --- |
| `DEFAULT_PROG` | `str = "task"` | pinned prog string (§4) |
| `build_parser` | `() -> argparse.ArgumentParser` | root parser: `prog=DEFAULT_PROG`, `description=…`; root `--file` with `metavar="PATH"`, `dest="storage_file"`, `default=None`; `subparsers = add_subparsers(dest="command", required=True)`; four subparsers per §4, each `set_defaults(handler=…)`; each subparser's `help=` is one sentence. |
| `main` | `(argv: Sequence[str] | None = None) -> int` | `parser = build_parser()`, `args = parser.parse_args(argv)` (argparse exits 2 on usage error), `return run(args)`. **Accepts no required arguments**, so it is a valid `[project.scripts]` entry point. |
| `run` | `(args: argparse.Namespace) -> int` | resolves the path (`args.storage_file or storage.default_path()`), dispatches `args.handler(args, path)` inside `try/except`, catches `storage.StorageError`, `storage.TaskNotFoundError`, `models.TaskDataError`, prints `task {args.command}: error: {exc}` to **stderr**, returns **1**. Unexpected exceptions propagate (traceback + exit 1 via the interpreter). |
| `cmd_add` | `(args: argparse.Namespace, path: Path) -> int` | validates title with the §4.1 rules → `storage.add_task` → prints `Added task {id}: {title}` to **stdout** → returns 0 |
| `cmd_list` | `(args: argparse.Namespace, path: Path) -> int` | `storage.read_tasks` → `sorted(tasks, key=lambda t: t.id)` → prints `No tasks yet.` if empty else one §4.2 line per task → returns 0 |
| `cmd_done` | `(args: argparse.Namespace, path: Path) -> int` | id `> 0` check → `storage.set_done(path, id, True)` → prints `Task {id} marked done.` → returns 0 |
| `cmd_delete` | `(args: argparse.Namespace, path: Path) -> int` | id `> 0` check → `storage.delete_task` → prints `Deleted task {id}.` → returns 0 |

Handler dispatch is `args.handler`, set by `set_defaults(handler=cmd_add)` etc. — the pattern the argparse docs endorse for `add_subparsers()` ("so each subparser knows which function to execute"). `required=True` on `add_subparsers()` is available since 3.7 and is mandatory here so that bare `task` exits 2 rather than doing nothing.

### 6.5 `taskcli/__main__.py`

Exactly three statements and nothing else — no `if __name__ == "__main__":` fence (unnecessary and discouraged inside a package `__main__`):

```text
"""Allow ``python -m taskcli``."""
import sys
from taskcli import cli
sys.exit(cli.main())
```

(Shown for contract only; the coder writes the file.) `python -m <package>` executes `<pkg>.__main__` as the main module — documented behavior.

### 6.6 `pyproject.toml` required content (described, not written by this document)

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "task-cli"
version = "0.1.0"
description = "A small command-line task manager backed by a single JSON file."
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
keywords = ["cli", "tasks", "todo", "json"]

[project.scripts]
task = "taskcli.cli:main"

[tool.setuptools]
packages = ["taskcli"]
```

- `requires-python = ">=3.11"` — the runtime is 3.15.2; 3.11 floors `argparse` subparser `required`, `dataclasses`, and `Path` behaviors used here while still allowing the `from __future__ import annotations` import to be a no-op.
- The `[project.scripts]` entry point `task = "taskcli.cli:main"` satisfies the PyPA requirement that the entry-point function accept no arguments and may return an int exit status (<https://packaging.python.org/en/latest/guides/creating-command-line-tools/>). `main()` parses `sys.argv[1:]` internally via `argparse` when `argv is None`.
- `packages = ["taskcli"]` is explicit rather than auto-discovered, so the flat layout (§2.1) cannot accidentally pick up stray directories.

---

## 7. Verification plan (deterministic smoke test — the critic runs these verbatim)

Precondition: working directory `<repo-root>/benchmarks/task-cli`, Python 3.15.2, **no install step**. All storage goes to a scratch file via `--file` so the test is repeatable and never touches `taskcli.json`. Every command's exit code is asserted. Run in PowerShell (the target platform); `$LASTEXITCODE` is read immediately after each command.

```powershell
$ROOT = "<repo-root>/benchmarks/task-cli"
$DATA = Join-Path $env:TEMP "taskcli_smoke.json"
Remove-Item $DATA -ErrorAction SilentlyContinue
Set-Location $ROOT

# V1 --help / bare invocation (usage errors exit 2, help exits 0)
python -m taskcli --help;                        "V1 exit=$LASTEXITCODE"   # expect 0, prints 'add', 'list', 'done', 'delete'
python -m taskcli;                               "V2 exit=$LASTEXITCODE"   # expect 2 (no subcommand)

# V3 add (twice), exact stdout, then exact JSON on disk
python -m taskcli --file $DATA add "Buy milk";   "V3 exit=$LASTEXITCODE"   # expect 0, 'Added task 1: Buy milk'
python -m taskcli --file $DATA add "Write design doc"; "V4 exit=$LASTEXITCODE"  # expect 0, 'Added task 2: Write design doc'
python -m taskcli --file $DATA list;             "V5 exit=$LASTEXITCODE"   # expect 0, two lines, '   1  [ ]  Buy milk  <ts>'

# V6 JSON validity + exact schema of the written file
python -c "import json,pathlib,sys; d=json.loads(pathlib.Path(r'$DATA').read_text(encoding='utf-8')); assert set(d)=={'version','tasks'}, d; assert d['version']==1; assert len(d['tasks'])==2; [assert_keys:=None]; import sys as s; ks=[set(t) for t in d['tasks']]; assert ks==[{'id','title','done','created_at'}]*2, ks; assert [t['id'] for t in d['tasks']]==[1,2]; assert all(t['done'] is False for t in d['tasks']); assert all(t['created_at'].endswith('Z') and len(t['created_at'])==20 for t in d['tasks']); print('V6 json-ok')"
"V6 exit=$LASTEXITCODE"                          # expect 0, 'V6 json-ok'
python -c "print(open(r'$DATA',encoding='utf-8').read()[-1] == chr(10))"   # V6b: expect True (single trailing newline)

# V7 done then list (exact done marker '[x]')
python -m taskcli --file $DATA done 1;           "V7 exit=$LASTEXITCODE"   # expect 0, 'Task 1 marked done.'
python -m taskcli --file $DATA list;             "V8 exit=$LASTEXITCODE"   # expect 0, line 1 is '   1  [x]  Buy milk  <ts>'
python -m taskcli --file $DATA done 1;           "V9 exit=$LASTEXITCODE"   # expect 0, idempotent, same output

# V10 unknown id (domain error, exit 1), non-integer id (usage error, exit 2)
python -m taskcli --file $DATA done 99  2>&1;    "V10 exit=$LASTEXITCODE"  # expect 1, 'task done: error: task 99 not found'
python -m taskcli --file $DATA delete 99 2>&1;   "V11 exit=$LASTEXITCODE"  # expect 1, 'task delete: error: task 99 not found'
python -m taskcli --file $DATA done abc  2>&1;   "V12 exit=$LASTEXITCODE"  # expect 2, argparse invalid int value
python -m taskcli --file $DATA done 0    2>&1;   "V13 exit=$LASTEXITCODE"  # expect 1, positive-integer domain error
python -m taskcli --file $DATA add ""    2>&1;   "V14 exit=$LASTEXITCODE"  # expect 1, title domain error
python -m taskcli --file $DATA bogus     2>&1;   "V15 exit=$LASTEXITCODE"  # expect 2, invalid choice

# V16-V21 delete / add in the main trace -- exercises the ID-REUSE RULING (§3.4 / §5.2)
python -m taskcli --file $DATA delete 2;         "V16 exit=$LASTEXITCODE"  # expect 0, 'Deleted task 2.'
python -m taskcli --file $DATA list;             "V17 exit=$LASTEXITCODE"  # expect 0, only id 1 remains, id 2 gone
python -m taskcli --file $DATA add "Third";      "V18 exit=$LASTEXITCODE"  # expect 0, 'Added task 2: Third'  (id 2 IS reused: it was the maximum, §5.2)
python -m taskcli --file $DATA delete 1;         "V19 exit=$LASTEXITCODE"  # expect 0, 'Deleted task 1.'
python -m taskcli --file $DATA delete 3;         "V20 exit=$LASTEXITCODE"  # expect 1, 'task delete: error: task 3 not found' (id 3 was never allocated)
python -m taskcli --file $DATA list;             "V21 exit=$LASTEXITCODE"  # expect 0, exactly one line: '   2  [ ]  Third  <ts>'

# V20b ID-REUSE RULING, self-contained on a fresh scratch file (§3.4 / §5.2)
$D2 = Join-Path $env:TEMP "taskcli_reuse.json"
Remove-Item $D2 -ErrorAction SilentlyContinue
python -m taskcli --file $D2 add "Alpha";        "V20b exit=$LASTEXITCODE" # expect 0, 'Added task 1: Alpha'
python -m taskcli --file $D2 add "Beta";         "V20b exit=$LASTEXITCODE" # expect 0, 'Added task 2: Beta'
python -m taskcli --file $D2 add "Gamma";        "V20b exit=$LASTEXITCODE" # expect 0, 'Added task 3: Gamma'
python -m taskcli --file $D2 delete 3;           "V20b exit=$LASTEXITCODE" # expect 0, 'Deleted task 3.'  (3 was the MAXIMUM id)
python -m taskcli --file $D2 add "Delta";        "V20b exit=$LASTEXITCODE" # expect 0, 'Added task 3: Delta'  (id 3 IS reused: max(1,2)+1)
python -m taskcli --file $D2 delete 1;           "V20b exit=$LASTEXITCODE" # expect 0, 'Deleted task 1.'  (1 is NOT the maximum; 2 and 3 survive)
python -m taskcli --file $D2 add "Epsilon";      "V20b exit=$LASTEXITCODE" # expect 0, 'Added task 4: Epsilon'  (id 1 is NOT reused: max(2,3)+1)
python -m taskcli --file $D2 list;               "V20b exit=$LASTEXITCODE" # expect 0, ids 2,3,4 ascending; no id 1
python -c "import json,pathlib; d=json.loads(pathlib.Path(r'$D2').read_text(encoding='utf-8')); assert [t['id'] for t in d['tasks']]==[2,3,4], [t['id'] for t in d['tasks']]; assert set(d)=={'version','tasks'}; print('V20b json-ok')"
python -m taskcli --file $D2 delete 4;           "V20b exit=$LASTEXITCODE" # expect 0, 'Deleted task 4.'
python -m taskcli --file $D2 delete 2;           "V20b exit=$LASTEXITCODE" # expect 0, 'Deleted task 2.'
python -m taskcli --file $D2 delete 3;           "V20b exit=$LASTEXITCODE" # expect 0, 'Deleted task 3.'
python -m taskcli --file $D2 list;               "V20b exit=$LASTEXITCODE" # expect 0, exactly 'No tasks yet.'  (existing file, empty tasks array)
Remove-Item $D2 -ErrorAction SilentlyContinue

# V22 missing file => treated as empty, exit 0, file created only on mutation
$MISSING = Join-Path $env:TEMP "taskcli_absent.json"
Remove-Item $MISSING -ErrorAction SilentlyContinue
python -m taskcli --file $MISSING list;          "V22 exit=$LASTEXITCODE"  # expect 0, 'No tasks yet.'
Test-Path $MISSING;                              "V23 expect False (read does not create the file)"

# V24 corrupt / unreadable storage file => exit 1, message on stderr
Set-Content -Path $DATA -Value "not json at all" -NoNewline
python -m taskcli --file $DATA list     2>&1;    "V24 exit=$LASTEXITCODE"  # expect 1, 'task list: error: cannot read storage file'
python -m taskcli --file $DATA add "x"  2>&1;    "V25 exit=$LASTEXITCODE"  # expect 1, same class of error
Set-Content -Path $DATA -Value "{}";      python -m taskcli --file $DATA list 2>&1     # V26 expect 1 (missing 'version'/'tasks')
Set-Content -Path $DATA -Value '{"version":2,"tasks":[]}'; python -m taskcli --file $DATA list 2>&1   # V27 expect 1 (bad version)
Set-Content -Path $DATA -Value '{"version":1,"tasks":[{"id":1,"title":"x","done":"false","created_at":"2026-01-01T00:00:00Z"}]}'
python -m taskcli --file $DATA list 2>&1;        "V28 exit=$LASTEXITCODE"  # expect 1 (done must be a boolean)
Set-Content -Path $DATA -Value '{"version":1,"tasks":[{"id":1,"title":"x","done":false}]}'
python -m taskcli --file $DATA list 2>&1;        "V29 exit=$LASTEXITCODE"  # expect 1 (missing created_at)
python -m taskcli --file $DATA list "extra" 2>&1 # V30 expect 2 (unexpected positional)

# V31 --file placement gotcha is exercised and matches §4.0
python -m taskcli add "y" --file $DATA 2>&1;     "V31 exit=$LASTEXITCODE"  # expect 2, 'unrecognized arguments: --file $DATA'

# V32a flat layout + zero install: from OUTSIDE the project root the package is NOT importable (expected)
Set-Location $env:TEMP
python -m taskcli --file $DATA list 2>&1;        "V32a exit=$LASTEXITCODE" # expect 1, 'No module named taskcli' (no sys.path hacks, §2.1)

# V32b zero-install module invocation FROM the project root (the supported form, §2.1)
Set-Content -Path $DATA -Value '{"version":1,"tasks":[]}'   # repair $DATA after the V24-V29 corruption block
Set-Location $ROOT
python -m taskcli --file $DATA list;             "V32b exit=$LASTEXITCODE" # expect 0, 'No tasks yet.' — proves `python -m taskcli` needs no install

# V33 no stray artifacts left behind (lock file and tmp files must be cleaned up)
Get-ChildItem -Path $env:TEMP -Filter "taskcli_*" -File | Select-Object -ExpandProperty Name   # expect only taskcli_smoke.json / taskcli_absent.json
Remove-Item $DATA -ErrorAction SilentlyContinue
```

Notes for the critic:

- `python -m taskcli --help` must exit **0** and print usage containing all four subcommand names; bare `python -m taskcli` must exit **2**.
- The per-task line separator is two spaces; the pending marker contains a single space inside the brackets (`[ ]`), the done marker is `[x]` with no space.
- `<ts>` in the expectations above is a 20-character `YYYY-MM-DDTHH:MM:SSZ` string, not a literal placeholder.
- Every stderr assertion must show **no traceback**.
- After V33, no `*.lock` or `.*.tmp` file may remain in the scratch directory or the project root.
- **Id-reuse ruling (§3.4 / §5.2) governs every id expectation in this plan.** V18 and V20b are the two places it is demonstrated: V18 shows `max(surviving)+1` reusing the just-deleted maximum, V20b shows both branches (maximum deleted → id reused; non-maximum deleted → id not reused at that point). Any expectation in this plan that implies an id is permanently retired is superseded by the ruling.
- V32a is a **expected failure** (exit 1, `No module named taskcli`); it proves the flat layout is honored with no `sys.path` manipulation. V32b is the supported invocation and must exit 0.

---

## 8. Sources

| URL | Quote / claim it supports |
| --- | --- |
| <https://docs.python.org/3/library/json.html> | "json.dump(obj, fp, *, indent=…, sort_keys=…, ensure_ascii=…, default=…)" and "json.load(fp, *, object_hook=…, object_pairs_hook=…)" — the stdlib JSON API used for the envelope; `json.JSONDecodeError` subclasses `ValueError`; `json` always produces `str`, so `fp.write()` must support `str`; UTF-8 encoding is recommended explicitly (PEP 597); "Newlines are only inserted via `indent`". |
| <https://docs.python.org/3/library/os.html#os.replace> | "os.replace" atomic-rename semantics and the warning that it "may fail if `src` and `dst` are on different filesystems" — basis for the temp file being created in the same directory as the target. `os.fsync` durability call in §5.3. |
| <https://docs.python.org/3/library/argparse.html> | "While argparse is the default recommended standard library module for implementing basic command line applications…" — choice of parser; `add_subparsers()` combined with `set_defaults()` "so each subparser knows which function to execute"; `add_subparsers(..., required=True)` (required added in 3.7); `parser.error()` "terminates the program with a status code of 2"; `type=int` conversion errors exit 2. |
| <https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers> | "If a subparser defines an argument with the same dest as the parent parser, the two share a single namespace attribute, so the parent's value won't be retained. Users should give them distinct dest values" — the distinct-dest rule for the global `--file` in §4.0. |
| <https://docs.python.org/3/using/cmdline.html#cmdoption-m> | `python -m <package>` runs `<pkg>.__main__` as the main module (§6.5); "Unix programs generally use 2 for command line syntax errors and 1 for all other kinds of errors" — the exit-code split in §4.5. |
| <https://docs.python.org/3/library/optparse.html#choosing-an-argument-parsing-library> | "argparse is the recommended choice…" — corroborates argparse; note that `optparse` is **not** currently marked deprecated in the 3.15.2 docs and `getopt` sits under "Superseded modules", so no deprecation argument is made either way. |
| <https://packaging.python.org/en/latest/guides/creating-command-line-tools/> | Flat vs src layout: `python -m greetings` "works immediately with flat layout, but requires installation of the package with src layout" (§2.1); `[project.scripts]` console entry points whose entry-point function "must accept no arguments", parses `sys.argv` with argparse inside, and "may return an int exit status" (§6.6). |
| <https://packaging.python.org/en/latest/tutorials/packaging-projects/> | `pyproject.toml`-based packaging with a build backend and `[project]` metadata (§6.6). |

### Statement about non-official practices

The atomic-write recipe in §5.3 (temp file in the same directory + `os.replace`) and the `O_EXCL`-based lock file in §5.4 are **community practice resting on documented primitives**, not documented patterns. They are used because they are strictly safer than the naive alternatives, and no verification step in §7 depends on their crash-safety guarantees being observable.

---

**End of DESIGN.md — awaiting approval before any code is written.**
