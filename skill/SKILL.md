---
name: docs-index
description: Build, refresh or read a project's `_INDEX.md`, the map of its Markdown docs that an agent opens first. Use when a project has no `_INDEX.md`, when `verify_index.py` reports coverage under 100%, or when a session starts in a project that has an index.
---

# docs-index

An index turns "explore the project" into "read one file, then open the three
documents that matter". The rules for the index are in
[INDEX_CONTRACT.md](INDEX_CONTRACT.md). The checker is `verify_index.py`: find
it next to this folder (`../verify_index.py`), or copy it beside this file and
call `python verify_index.py <project>`.

## Read an index

1. Open `_INDEX.md` before listing directories.
2. Open only the documents that "Start here" and the map name for your task.
3. Run `python verify_index.py <project>` once. Coverage under 100% means some
   files are unmapped: treat them as unknown and say so in your answer.
4. When you add, move or rename a `.md` file, update the index in the same task
   and run the checker again.

## Build or refresh an index

Done means: the checker exits 0 and the reviewer reports no must-fix.

1. **Inventory.** Create an empty `_INDEX.md` and run the checker. Its
   `[not-linked]` lines are the complete list of files to map.
2. **Map.** Read each file. Record `path | category | what is inside | flags`
   (flags: empty, stale, duplicate, superseded). The summary comes from the
   file text, not from its name. Large projects: give each subagent a batch of
   about 40 files.
3. **Build.** Write `_INDEX.md` from the mapped rows, following the contract.
4. **Review.** A different agent, with fresh context, opens the index and
   checks ten claims against the files. It returns a list of must-fix items
   and should-fix items. The builder does not review its own index.
5. **Verify.** Run the checker. Fix what it names, rerun, repeat until exit 0.
   Fix what the reviewer marked must-fix, then run the checker once more.

## Who does which phase

| Phase | Model tier | Why |
|---|---|---|
| Map | economical | Many files, each read is independent and routine |
| Build, project up to about 60 docs | economical | The synthesis fits in one head |
| Build, larger project or a folder of projects | more capable | "In brief", "Start here" and "Gaps" must hold hundreds of facts at once |
| Review | economical | Spot-checking a claim against a file is routine |
| Fix | economical | Only the named problems change |
| Verify | no model | A script counts links |

The thresholds (40 files per batch, 60 docs) are rules of thumb from one
author's setup, not tuned values. In that setup the economical tier was
Sonnet and the more capable tier was Opus. Start a subagent only when batches
can run in parallel: each one adds cost.

## Why the last check is a script

"Every file is linked" is a rule you count. A model follows it nearly always;
a script follows it always and names the file that is missing. The reviewer
keeps the rules you cannot count: whether "In brief" is true and whether a row
says what the file really holds. A script cannot judge those, and a model
should not be trusted with the counting.
