# Index contract

The rules every `_INDEX.md` follows. Two kinds of rule: the script enforces the
first kind, a reviewing model checks the second kind.

## Enforced by `verify_index.py`

1. The index is `_INDEX.md` at the project root.
2. Every `.md` file in the project is linked from it, once or more. The index
   itself and the skipped folders (`.git`, `node_modules`, `.venv`, `venv`,
   `__pycache__`, `.pytest_cache`, `.next`, `dist`, `build`, plus any
   `--exclude` folder) are not counted.
3. Every link points to a file or folder that exists. Letter case must match.
4. Every link is relative to the project root: `[Title](docs/api.md)`.
   Spaces go as `%20` or the path goes in angle brackets:
   `[Title](<docs/my file.md>)`.
5. No link leaves the project folder. Relations to other projects are written
   as text, without a link.

## Checked by the reviewer, not by the script

1. **In brief**: two to five sentences. What the project is, its stack, its
   current state with the evidence (latest handoff, latest phase).
2. **Start here**: three to seven documents in reading order, each with the
   reason to read it first.
3. **Map**: one table row per document, grouped by purpose (overview and setup,
   architecture and decisions, specification and operations, log and history).
   The second column says what is inside the file. A row that only restates the
   file name fails review.
4. **Gaps**: missing documents, documents that contradict each other, documents
   known to be stale (with the proof). Write "none found" when true.
5. A claim in the index that the files do not support is a must-fix.

## Skeleton

```markdown
# <Project>: documentation index

> In brief
> ...

> Start here
> 1. [README.md](README.md): why first

## Map

### Overview and setup
| Document | What is inside |
|---|---|
| [README.md](README.md) | ... |

## Gaps

- ...
```

A working example that passes the script is in `example/brindle/_INDEX.md`.
