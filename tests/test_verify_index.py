"""Tests for verify_index.py. Written before the implementation."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import verify_index
from verify_index import IndexNotFound, verify

REPO = Path(__file__).resolve().parent.parent


def make_project(root: Path, files: dict) -> Path:
    """Create files under root. Keys are relative paths, values are text."""
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def kinds(report) -> list:
    return sorted(issue.kind for issue in report.issues)


# --- complete coverage -------------------------------------------------------


def test_full_coverage_passes_with_100_percent(tmp_path):
    project = make_project(tmp_path, {
        "_INDEX.md": "[Readme](README.md)\n[Design](docs/design.md)\n",
        "README.md": "# Readme\n",
        "docs/design.md": "# Design\n",
    })
    report = verify(project)
    assert report.coverage == 100.0
    assert report.issues == []
    assert report.ok is True
    assert report.expected == ["README.md", "docs/design.md"]
    assert report.linked == ["README.md", "docs/design.md"]


def test_project_with_only_an_index_is_fully_covered(tmp_path):
    project = make_project(tmp_path, {"_INDEX.md": "# Nothing to map\n"})
    report = verify(project)
    assert report.expected == []
    assert report.coverage == 100.0
    assert report.ok is True


def test_fragment_in_link_still_counts_as_linked(tmp_path):
    project = make_project(tmp_path, {
        "_INDEX.md": "[API](api.md#auth)\n",
        "api.md": "# API\n",
    })
    assert verify(project).ok is True


# --- not linked --------------------------------------------------------------


def test_unlinked_file_fails_and_is_named(tmp_path):
    project = make_project(tmp_path, {
        "_INDEX.md": "[Readme](README.md)\n",
        "README.md": "# Readme\n",
        "HANDOFF.md": "# Handoff\n",
    })
    report = verify(project)
    assert report.ok is False
    assert report.coverage == 50.0
    assert kinds(report) == ["not-linked"]
    assert report.issues[0].detail == "HANDOFF.md"


def test_coverage_never_rounds_up_to_100_on_a_failing_run(tmp_path):
    files = {"_INDEX.md": "".join(f"[d{i}](d{i}.md)\n" for i in range(299))}
    for i in range(300):
        files[f"d{i}.md"] = "x\n"
    report = verify(make_project(tmp_path, files))
    assert report.ok is False
    assert report.coverage < 100.0


def test_same_file_name_in_two_folders_needs_two_links(tmp_path):
    project = make_project(tmp_path, {
        "_INDEX.md": "[A](a/README.md)\n",
        "a/README.md": "x\n",
        "b/README.md": "y\n",
    })
    report = verify(project)
    assert [i.detail for i in report.issues] == ["b/README.md"]


def test_the_index_itself_is_not_expected_to_be_linked(tmp_path):
    project = make_project(tmp_path, {"_INDEX.md": "", "a.md": "x\n"})
    assert "_INDEX.md" not in verify(project).expected


# --- broken links ------------------------------------------------------------


def test_broken_link_fails_and_reports_the_line(tmp_path):
    project = make_project(tmp_path, {
        "_INDEX.md": "# Title\n\n[Gone](docs/missing.md)\n",
    })
    report = verify(project)
    assert kinds(report) == ["broken-link"]
    assert report.issues[0].source == "_INDEX.md:3"
    assert report.issues[0].detail == "docs/missing.md"
    assert report.ok is False


def test_link_with_wrong_letter_case_is_broken_on_every_os(tmp_path):
    project = make_project(tmp_path, {
        "_INDEX.md": "[Readme](readme.md)\n",
        "README.md": "x\n",
    })
    report = verify(project)
    assert kinds(report) == ["broken-link", "not-linked"]


def test_link_to_an_existing_folder_or_non_markdown_file_is_fine(tmp_path):
    project = make_project(tmp_path, {
        "_INDEX.md": "[Docs](docs/)\n[Schema](schema.sql)\n",
        "docs/.keep": "",
        "schema.sql": "select 1;\n",
    })
    assert verify(project).ok is True


# --- link style --------------------------------------------------------------


@pytest.mark.parametrize("target", [
    "/opt/docs/a.md",
    "D:/data/a.md",
    "D:\\data\\a.md",
    "\\\\server\\share\\a.md",
    "file:///opt/docs/a.md",
])
def test_absolute_links_fail(tmp_path, target):
    project = make_project(tmp_path, {
        "_INDEX.md": f"[A](<{target}>)\n[Real](a.md)\n",
        "a.md": "x\n",
    })
    report = verify(project)
    assert kinds(report) == ["absolute-link"]
    assert report.ok is False


def test_link_that_leaves_the_project_fails(tmp_path):
    (tmp_path / "other").mkdir()
    (tmp_path / "other" / "README.md").write_text("x\n", encoding="utf-8")
    project = make_project(tmp_path / "proj", {
        "_INDEX.md": "[Other](../other/README.md)\n",
    })
    assert kinds(verify(project)) == ["outside-project"]


def test_percent_encoded_and_angle_bracket_paths_resolve(tmp_path):
    project = make_project(tmp_path, {
        "_INDEX.md": "[One](notes/one%20two.md)\n[Two](<notes/three four.md>)\n",
        "notes/one two.md": "x\n",
        "notes/three four.md": "y\n",
    })
    assert verify(project).ok is True


def test_link_with_title_text_is_parsed(tmp_path):
    project = make_project(tmp_path, {
        "_INDEX.md": '[A](a.md "Tooltip")\n',
        "a.md": "x\n",
    })
    assert verify(project).ok is True


def test_urls_anchors_images_and_code_are_not_links(tmp_path):
    project = make_project(tmp_path, {
        "_INDEX.md": (
            "[Web](https://example.org/x.md)\n"
            "[Mail](mailto:someone)\n"
            "[Here](#top)\n"
            "![Pic](images/none.png)\n"
            "Inline `[x](missing-inline.md)` is code.\n"
            "```\n"
            "[y](missing-fenced.md)\n"
            "```\n"
            "[Real](a.md)\n"
        ),
        "a.md": "x\n",
    })
    assert verify(project).ok is True


# --- excluded folders --------------------------------------------------------


def test_default_excluded_folders_are_not_expected(tmp_path):
    project = make_project(tmp_path, {
        "_INDEX.md": "[A](a.md)\n",
        "a.md": "x\n",
        "node_modules/pkg/README.md": "x\n",
        ".git/notes.md": "x\n",
        "src/__pycache__/n.md": "x\n",
    })
    report = verify(project)
    assert report.expected == ["a.md"]
    assert report.ok is True


def test_extra_excluded_folder_is_not_expected(tmp_path):
    files = {
        "_INDEX.md": "[A](a.md)\n",
        "a.md": "x\n",
        "generated/out.md": "x\n",
    }
    project = make_project(tmp_path, files)
    assert verify(project).ok is False
    assert verify(project, exclude=["generated"]).ok is True


def test_hidden_folders_are_mapped_unless_excluded(tmp_path):
    project = make_project(tmp_path, {
        "_INDEX.md": "[A](a.md)\n",
        "a.md": "x\n",
        ".notes/plan.md": "x\n",
    })
    assert kinds(verify(project)) == ["not-linked"]


# --- missing index -----------------------------------------------------------


def test_missing_index_raises(tmp_path):
    with pytest.raises(IndexNotFound):
        verify(tmp_path)


# --- command line ------------------------------------------------------------


def test_cli_exit_codes_and_output(tmp_path, capsys):
    ok = make_project(tmp_path / "ok", {"_INDEX.md": "[A](a.md)\n", "a.md": "x\n"})
    assert verify_index.main([str(ok)]) == 0
    out = capsys.readouterr().out
    assert "Coverage: 1/1 .md files linked (100.0%)" in out
    assert out.strip().endswith("PASS")

    bad = make_project(tmp_path / "bad", {"_INDEX.md": "", "a.md": "x\n"})
    assert verify_index.main([str(bad)]) == 1
    out = capsys.readouterr().out
    assert "Coverage: 0/1 .md files linked (0.0%)" in out
    assert "[not-linked] a.md" in out
    assert out.strip().endswith("FAIL")


def test_cli_exit_code_2_when_index_is_missing(tmp_path, capsys):
    assert verify_index.main([str(tmp_path)]) == 2
    assert "no _INDEX.md" in capsys.readouterr().err


def test_cli_exclude_flag(tmp_path):
    project = make_project(tmp_path, {
        "_INDEX.md": "[A](a.md)\n", "a.md": "x\n", "gen/o.md": "x\n",
    })
    assert verify_index.main([str(project)]) == 1
    assert verify_index.main([str(project), "--exclude", "gen"]) == 0


def test_cli_output_is_ascii_and_sorted(tmp_path, capsys):
    project = make_project(tmp_path, {"_INDEX.md": "", "b.md": "x\n", "a.md": "x\n"})
    verify_index.main([str(project)])
    out = capsys.readouterr().out
    out.encode("ascii")
    assert out.index("a.md") < out.index("b.md")


# --- the shipped example -----------------------------------------------------


def test_example_project_passes():
    report = verify(REPO / "example" / "brindle")
    assert report.coverage == 100.0
    assert report.issues == []
    assert 6 <= len(report.expected) <= 10


def test_example_with_errors_shows_every_error_kind():
    report = verify(REPO / "example" / "brindle-with-errors")
    assert report.ok is False
    assert set(kinds(report)) == {
        "not-linked", "broken-link", "absolute-link", "outside-project",
    }


def test_cli_runs_as_a_script_with_exit_codes():
    script = str(REPO / "verify_index.py")
    good = subprocess.run(
        [sys.executable, script, str(REPO / "example" / "brindle")],
        capture_output=True, text=True,
    )
    bad = subprocess.run(
        [sys.executable, script, str(REPO / "example" / "brindle-with-errors")],
        capture_output=True, text=True,
    )
    assert good.returncode == 0
    assert bad.returncode == 1
