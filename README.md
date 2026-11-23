[Italiano](README.it.md)

# docs-index-for-agents

A documentation index that a coding agent reads first, a script that checks the index covers every file, and a Claude Code skill that tells an agent how to build and maintain it.

Author: Lorenzo Algeri. License: MIT.

## An index the agent reads before anything else

A project that Claude Code works on every day collects a lot of Markdown: plans, decisions, handoff notes, runbooks. At the start of a session the agent doesn't know which files are current. It lists folders, opens the wrong files or reads too much, and that eats context window before any real work starts.

So I keep one file, `_INDEX.md`, at the root of each project. It says what the project is, where to start and what every document really contains, and the agent is told to read it first.

A script checks the index. "Every `.md` file is linked, every link works, every link is relative" is easy to count, so the script counts it. What it can't tell me is whether the one-line summaries are true. That part I give to a model to review.

| Path | What it is |
|---|---|
| `verify_index.py` | The checker. Python standard library only. |
| `tests/test_verify_index.py` | 30 pytest tests, written before the code. |
| `example/brindle/` | An invented project (8 `.md` files) with a correct index. |
| `example/brindle-with-errors/` | The same project, with the index broken on purpose. |
| `skill/SKILL.md` | Claude Code skill: how to read, build and refresh an index, and which phase runs on which model tier. |
| `skill/INDEX_CONTRACT.md` | One page: what the script enforces and what the reviewer checks. |

## Try it in 5 minutes

You need Python 3.9 or newer (I developed and tested it on 3.13 only). On macOS and Linux the command may be `python3`.

```text
python -m pip install pytest
python -m pytest
python verify_index.py example/brindle
python verify_index.py example/brindle-with-errors
```

Output on the correct example (exit code 0):

```text
Project: example/brindle
Index: _INDEX.md
Coverage: 8/8 .md files linked (100.0%)
PASS
```

Output on the broken example (exit code 1):

```text
Project: example/brindle-with-errors
Index: _INDEX.md
Coverage: 5/8 .md files linked (62.5%)
Errors (6):
  [absolute-link] _INDEX.md:32 -> /srv/brindle/docs/api.md
  [broken-link] _INDEX.md:33 -> docs/run-book.md
  [outside-project] _INDEX.md:39 -> ../brindle/README.md
  [not-linked] CHANGELOG.md
  [not-linked] docs/api.md
  [not-linked] docs/runbook.md
FAIL
```

I planted four mistakes: an absolute link, a link with a typo, a link to another project and a file left out. The absolute link and the typo also leave their file unlinked, so you see six lines.

Options: `--index NAME` uses another index file name, `--exclude DIR` (repeatable) skips a folder. Exit code 2 means the index file is missing.

Coverage is printed as a floored percentage next to the counts, so a failing run never shows `100.0%`. Link targets are compared with exact letter case, so a link that works on Windows but breaks on Linux fails here.

## Numbers from the original system

I use the original system on my own working folders. These numbers come from personal use and were measured by the original verifier, which does more than the smaller rewrite in this repo. You can't reproduce them from here, and they are not a benchmark.

| Measure | Value | Date |
|---|---|---|
| First generation | 59 indexes, 3876 `.md` files mapped | 5-7 Oct 2026 |
| Scope | 80 projects and 3 containers, 6585 `.md` files | 20 Nov 2026 |
| Coverage | 4684 of 5316 expected `.md` files linked (88%), counted over the entries that have an index | 20 Nov 2026 |
| Entries with errors | 24 of 83, of which 16 have no index (some are service folders, not projects) | 20 Nov 2026 |
| Time saved at session start | not measured | |
| Token cost of generating the indexes | not measured | |

The 88% is what I learned the most from. My global rule for the agent says "update the index when you change docs", and the checker shows the rule alone doesn't hold: indexes drift. The likely cause is files written after the last regeneration. I didn't check that file by file.

## What the original verifier does on top

The original verifier also supports sub-indexes for very large projects and checks front matter and section headings. Those checks are not here. I also left out the original's orchestration script. The skill describes the phases and the model tiers in prose, so you apply it as a method with your own subagent setup. It is not a tested workflow.

## Limits

- The checker only looks at structure. An index row that describes a file wrongly still passes. Catching that is the reviewer's job, and the reviewer is a model.
- It reads one index file at the project root.
- It follows inline links `[text](path)`. Reference-style links are not parsed.
- I have no measurement showing that an index saves time or tokens. That a session wastes context without one is the idea I started from. I haven't proved it.
- Not built yet: a hook that runs the checker at the end of a session, so I don't have to rely on a written rule.

## License

MIT. See `LICENSE`.
