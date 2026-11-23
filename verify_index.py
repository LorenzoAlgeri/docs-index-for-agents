#!/usr/bin/env python3
"""Check that a project's _INDEX.md covers every Markdown file in the project.

Usage:
    python verify_index.py PROJECT_DIR [--index _INDEX.md] [--exclude DIR ...]

Checks, in plain code with no model in the loop:
  1. every .md file in the project is linked from the index (coverage);
  2. every link in the index points to a file or folder that exists;
  3. every link is relative (no /abs, no D:/abs, no file: URL);
  4. no link leaves the project folder.

Exit code: 0 all checks pass, 1 at least one check fails, 2 usage error.
Standard library only.
"""
from __future__ import annotations

import argparse
import math
import os
import posixpath
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

DEFAULT_EXCLUDED = frozenset({
    ".git", "node_modules", ".venv", "venv", "__pycache__",
    ".pytest_cache", ".next", "dist", "build",
})

# [text](target), [text](<target with spaces>), optional "title"; images excluded.
LINK_RE = re.compile(
    r"(?<!!)\[[^\]]*\]\(\s*(<[^>]*>|[^)\s]*)(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)"
)
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
DRIVE_RE = re.compile(r"^[A-Za-z]:[/\\]")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


class IndexNotFound(Exception):
    """The project has no index file."""


@dataclass
class Issue:
    kind: str    # not-linked | broken-link | absolute-link | outside-project
    source: str  # "_INDEX.md:14" for link problems, "" for not-linked
    detail: str  # the link target, or the file that is not linked


@dataclass
class Report:
    expected: list = field(default_factory=list)  # .md files that must be linked
    linked: list = field(default_factory=list)    # of those, the ones that are
    issues: list = field(default_factory=list)

    @property
    def coverage(self) -> float:
        """Percent of expected files linked, floored so a failure never shows 100.0."""
        if not self.expected:
            return 100.0
        return math.floor(1000 * len(self.linked) / len(self.expected)) / 10

    @property
    def ok(self) -> bool:
        return not self.issues


def _is_absolute(target: str) -> bool:
    return (
        target.startswith(("/", "\\"))
        or bool(DRIVE_RE.match(target))
        or target.lower().startswith("file:")
    )


def _links(text: str):
    """Yield (line_number, target) for links outside code fences and inline code."""
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), line)
        for match in LINK_RE.finditer(line):
            yield number, match.group(1).strip("<>")


def _markdown_files(root: Path, excluded: set) -> list:
    found = []
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in excluded)
        for name in sorted(files):
            if name.lower().endswith(".md"):
                rel = Path(folder, name).relative_to(root)
                found.append(rel.as_posix())
    return sorted(found)


class _ExactPaths:
    """Existence check that is case-exact on every OS (Linux is, Windows is not)."""

    def __init__(self, root: Path):
        self.root = root
        self._listings: dict = {}

    def _names(self, rel_dir: str) -> set:
        if rel_dir not in self._listings:
            try:
                self._listings[rel_dir] = set(os.listdir(self.root / rel_dir))
            except OSError:
                self._listings[rel_dir] = set()
        return self._listings[rel_dir]

    def exists(self, rel: str) -> bool:
        current = ""
        for part in rel.split("/"):
            if part not in self._names(current):
                return False
            current = posixpath.join(current, part)
        return True


def verify(project, index: str = "_INDEX.md", exclude=()) -> Report:
    root = Path(project)
    index_path = root / index
    if not index_path.is_file():
        raise IndexNotFound(f"no {index} in {project}")

    excluded = set(DEFAULT_EXCLUDED) | set(exclude)
    expected = [p for p in _markdown_files(root, excluded) if p != index]
    exact = _ExactPaths(root)
    issues: list = []
    linked: set = set()

    text = index_path.read_text(encoding="utf-8", errors="replace")
    for number, raw in _links(text):
        where = f"{index}:{number}"
        if raw.startswith("#"):
            continue
        if _is_absolute(raw):
            issues.append(Issue("absolute-link", where, raw))
            continue
        if SCHEME_RE.match(raw):  # http:, https:, mailto: ...
            continue
        target = unquote(raw.split("#", 1)[0]).replace("\\", "/")
        if not target:
            continue
        rel = posixpath.normpath(target)
        if rel == ".." or rel.startswith("../"):
            issues.append(Issue("outside-project", where, raw))
        elif not exact.exists(rel):
            issues.append(Issue("broken-link", where, raw))
        else:
            linked.add(rel)

    covered = [p for p in expected if p in linked]
    for path in expected:
        if path not in linked:
            issues.append(Issue("not-linked", "", path))
    return Report(expected=expected, linked=covered, issues=issues)


def _format(report: Report, project: str, index: str) -> str:
    lines = [
        f"Project: {project}",
        f"Index: {index}",
        f"Coverage: {len(report.linked)}/{len(report.expected)} .md files linked "
        f"({report.coverage:.1f}%)",
    ]
    if report.issues:
        lines.append(f"Errors ({len(report.issues)}):")
        for issue in report.issues:
            if issue.source:
                lines.append(f"  [{issue.kind}] {issue.source} -> {issue.detail}")
            else:
                lines.append(f"  [{issue.kind}] {issue.detail}")
    lines.append("PASS" if report.ok else "FAIL")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that _INDEX.md links every .md file of a project."
    )
    parser.add_argument("project", help="project folder that contains the index")
    parser.add_argument("--index", default="_INDEX.md", help="index file name")
    parser.add_argument(
        "--exclude", action="append", default=[], metavar="DIR",
        help="extra folder name to skip (repeatable)",
    )
    args = parser.parse_args(argv)
    try:
        report = verify(args.project, index=args.index, exclude=args.exclude)
    except IndexNotFound as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(_format(report, args.project.replace("\\", "/"), args.index))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
