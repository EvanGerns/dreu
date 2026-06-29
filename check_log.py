#!/usr/bin/env python3
"""
check_log.py — DREU weekly log format validator

Students: run this to check any single week file before pushing.

    python check_log.py logs/week-03.md

Exit code 0 = pass, 1 = validation errors found.
"""

import re
import sys
from pathlib import Path

# ── Format constants ──────────────────────────────────────────────────────────

REQUIRED_SECTIONS = [
    "Goals",
    "Approach and Implementation",
    "Results",
]

WEEK_TITLE_RE  = re.compile(r'^#\s+Week\s+\d+\s*$')
DATES_LINE_RE  = re.compile(
    r'^\*\*Dates:\*\*\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})\s*$'
)
PLACEHOLDER_RE = re.compile(r'YYYY-MM-DD')


# ── Core validator ────────────────────────────────────────────────────────────

def validate_log(content: str, filename: str = "") -> tuple[bool, list[str]]:
    """
    Validate the content of a weekly log file.

    Returns:
        (passed, errors)  — passed is True only when errors is empty.
    """
    lines  = content.splitlines()
    errors = []

    # 1. H1 title: must be "# Week N"
    h1_lines = [l for l in lines if l.startswith("# ")]
    if not h1_lines:
        errors.append("Missing H1 title — expected '# Week N' (e.g., '# Week 3')")
    elif not WEEK_TITLE_RE.match(h1_lines[0]):
        errors.append(
            f"H1 title must be '# Week N' with a number — found: '{h1_lines[0]}'"
        )

    # 2. Dates field: must be filled in and correctly formatted
    dates_lines = [l for l in lines if l.startswith("**Dates:**")]
    if not dates_lines:
        errors.append(
            "Missing Dates field — expected '**Dates:** YYYY-MM-DD to YYYY-MM-DD'"
        )
    else:
        dl = dates_lines[0]
        if PLACEHOLDER_RE.search(dl):
            errors.append("Dates field still contains placeholder — fill in the actual dates")
        elif not DATES_LINE_RE.match(dl):
            errors.append(
                f"Dates field format invalid — expected '**Dates:** YYYY-MM-DD to YYYY-MM-DD', found: '{dl}'"
            )

    # 3. Parse H2 sections and their content
    sections: dict[str, list[str]] = {}
    current: str | None = None
    body: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current is not None:
                sections[current] = body
            current = line[3:].strip()
            body = []
        elif current is not None:
            body.append(line)
    if current is not None:
        sections[current] = body

    # 4. Required sections must exist and contain non-empty content
    for section in REQUIRED_SECTIONS:
        if section not in sections:
            errors.append(f"Missing required section: '## {section}'")
        else:
            filled = [l for l in sections[section] if l.strip()]
            if not filled:
                errors.append(f"Section '## {section}' is empty — add your content")

    return (len(errors) == 0), errors


# ── File helper (used by both this script and check_all.py) ──────────────────

def validate_file(filepath: str | Path) -> tuple[bool, list[str]]:
    """Read a file from disk and validate it."""
    path = Path(filepath)
    if not path.exists():
        return False, [f"File not found: {filepath}"]
    content = path.read_text(encoding="utf-8")
    return validate_log(content, filename=path.name)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) != 2:
        print("Usage: python check_log.py logs/week-NN.md")
        sys.exit(1)

    filepath = sys.argv[1]
    passed, errors = validate_file(filepath)

    if passed:
        print(f"✓  {filepath} — format OK")
        sys.exit(0)
    else:
        print(f"✗  {filepath} — {len(errors)} issue(s) found:\n")
        for err in errors:
            print(f"   • {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
