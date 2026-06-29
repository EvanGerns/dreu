#!/usr/bin/env python3
"""
check_all.py — DREU coordinator script

Reads students.csv, fetches each student's GitHub repo or Google Doc, validates
all weekly logs due so far, prints a status summary, and (optionally) emails
students whose logs are missing or malformed.

Usage:
    python check_all.py                   # check and print report only
    python check_all.py --send-email      # check and email students with issues
    python check_all.py --week 4          # override current week (default: auto)

Supports two journal types (auto-detected from the URL in students.csv):
    GitHub repo   — https://github.com/username/repo
    Google Doc    — https://docs.google.com/document/d/DOC_ID/...
                    (must be shared as "Anyone with the link can view")

Requires:
    pip install requests
"""

import argparse
import configparser
import csv
import re
import smtplib
import sys
from datetime import date, timedelta
from email.message import EmailMessage
from pathlib import Path

import requests

from check_log import validate_log

# ── Config ────────────────────────────────────────────────────────────────────

CONFIG_FILE   = Path("config.ini")
STUDENTS_FILE = Path("students.csv")
NUM_WEEKS     = 10
BRANCH_ORDER  = ["main", "master"]   # tried in order when fetching from GitHub


def load_config() -> configparser.ConfigParser:
    if not CONFIG_FILE.exists():
        print(f"Error: {CONFIG_FILE} not found. Copy config.ini.template and fill it in.")
        sys.exit(1)
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILE)
    return cfg


# ── Week calculation ──────────────────────────────────────────────────────────

def current_week_number(start_date: date, today: date = None) -> int:
    """Return the current 1-based week number (capped at NUM_WEEKS)."""
    if today is None:
        today = date.today()
    delta = (today - start_date).days
    if delta < 0:
        return 0
    week = delta // 7 + 1
    return min(week, NUM_WEEKS)


# ── GitHub fetching ───────────────────────────────────────────────────────────

def raw_url(repo_url: str, filepath: str, branch: str) -> str:
    """Convert a GitHub repo URL to a raw content URL."""
    repo_url = repo_url.rstrip("/").removesuffix(".git")
    # https://github.com/user/repo  →  https://raw.githubusercontent.com/user/repo/branch/filepath
    parts = repo_url.replace("https://github.com/", "").split("/")
    if len(parts) < 2:
        return ""
    user, repo = parts[0], parts[1]
    return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{filepath}"


def fetch_file(repo_url: str, filepath: str, token: str = "") -> str | None:
    """
    Fetch a file from a GitHub repo. Returns content string or None if not found.
    Pass a GitHub personal access token for private repos.
    """
    headers = {"Authorization": f"token {token}"} if token else {}
    for branch in BRANCH_ORDER:
        url = raw_url(repo_url, filepath, branch)
        if not url:
            return None
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.text
    return None


# ── Google Docs fetching ─────────────────────────────────────────────────────

GDOC_ID_RE = re.compile(r"/document/d/([a-zA-Z0-9_-]+)")
WEEK_HEADING_RE = re.compile(r"^#\s+Week\s+(\d+)\s*$", re.MULTILINE)


def is_gdoc_url(url: str) -> bool:
    return "docs.google.com/document" in url


def gdoc_export_url(url: str) -> str:
    """Return the plain-text export URL for a Google Doc share link."""
    m = GDOC_ID_RE.search(url)
    if not m:
        return ""
    doc_id = m.group(1)
    return f"https://docs.google.com/document/d/{doc_id}/export?format=txt"


def fetch_gdoc(url: str) -> str | None:
    """
    Download a Google Doc as plain text. Returns None if inaccessible.
    The doc must be shared as "Anyone with the link can view".
    """
    export_url = gdoc_export_url(url)
    if not export_url:
        return None
    try:
        resp = requests.get(export_url, timeout=15, allow_redirects=True)
    except requests.RequestException:
        return None
    if resp.status_code != 200:
        return None
    # Normalise Windows line endings that Google sometimes returns
    return resp.text.replace("\r\n", "\n").replace("\r", "\n")


def split_gdoc_by_week(content: str) -> dict[int, str]:
    """
    Split a Google Doc into per-week sections.

    Splits on '# Week N' headings (the same format used in the Markdown template).
    Returns {week_number: section_text} for every week found.
    """
    weeks: dict[int, str] = {}
    # Find all heading positions
    matches = list(WEEK_HEADING_RE.finditer(content))
    for i, m in enumerate(matches):
        week_num = int(m.group(1))
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        weeks[week_num] = content[start:end].strip()
    return weeks


def check_student_gdoc(name: str, doc_url: str, weeks_due: int) -> list[dict]:
    """Validate all weeks in a student's Google Doc."""
    content = fetch_gdoc(doc_url)

    if content is None:
        error = (
            "Could not fetch Google Doc — confirm it is shared as "
            "'Anyone with the link can view'"
        )
        return [
            {"week": w, "status": STATUS_MISSING if w <= weeks_due else STATUS_FUTURE,
             "errors": [error] if w <= weeks_due else []}
            for w in range(1, NUM_WEEKS + 1)
        ]

    week_sections = split_gdoc_by_week(content)
    results = []

    for week in range(1, NUM_WEEKS + 1):
        if week > weeks_due:
            results.append({"week": week, "status": STATUS_FUTURE, "errors": []})
            continue

        if week not in week_sections:
            results.append({"week": week, "status": STATUS_MISSING, "errors": [
                f"Week {week} section not found in Google Doc "
                f"(expected a line '# Week {week}')"
            ]})
        else:
            passed, errors = validate_log(week_sections[week], filename=f"Week {week}")
            results.append({
                "week":   week,
                "status": STATUS_OK if passed else STATUS_INVALID,
                "errors": errors,
            })

    return results


# ── Per-student check ─────────────────────────────────────────────────────────

STATUS_OK      = "✓"
STATUS_MISSING = "MISSING"
STATUS_INVALID = "INVALID"
STATUS_FUTURE  = "—"       # week not yet due


def check_student(name: str, repo_url: str, weeks_due: int, token: str = "") -> list[dict]:
    """
    Check all logs for one student up to weeks_due.

    Returns a list of result dicts, one per week:
        { week, status, errors }
    """
    results = []
    for week in range(1, NUM_WEEKS + 1):
        if week > weeks_due:
            results.append({"week": week, "status": STATUS_FUTURE, "errors": []})
            continue

        filepath = f"logs/week-{week:02d}.md"
        content  = fetch_file(repo_url, filepath, token=token)

        if content is None:
            results.append({"week": week, "status": STATUS_MISSING, "errors": [
                f"logs/week-{week:02d}.md not found in repo"
            ]})
        else:
            passed, errors = validate_log(content, filename=filepath)
            results.append({
                "week":   week,
                "status": STATUS_OK if passed else STATUS_INVALID,
                "errors": errors,
            })

    return results


# ── Report printing ───────────────────────────────────────────────────────────

def print_report(students_results: list[dict], weeks_due: int):
    """Print a summary table to stdout."""
    col_w = 22
    week_headers = "  ".join(f"W{w:02d}" for w in range(1, NUM_WEEKS + 1))
    print(f"\n{'=' * 80}")
    print(f"DREU Journal Status Report — Weeks due: 1–{weeks_due}")
    print(f"{'=' * 80}")
    print(f"{'Name':<{col_w}}  {week_headers}")
    print(f"{'-' * col_w}  {'-' * (NUM_WEEKS * 5 - 2)}")

    for sr in students_results:
        row = f"{sr['name']:<{col_w}}  "
        for r in sr["results"]:
            s = r["status"]
            cell = {
                STATUS_OK:      " ✓ ",
                STATUS_MISSING: "MIS",
                STATUS_INVALID: "INV",
                STATUS_FUTURE:  " — ",
            }.get(s, " ? ")
            row += f"{cell}  "
        print(row)

    print(f"\nLegend: ✓=OK  MIS=missing  INV=invalid format  —=not yet due\n")

    # Detail for any issues
    any_issues = False
    for sr in students_results:
        issues = [(r["week"], r["errors"]) for r in sr["results"] if r["errors"]]
        if issues:
            if not any_issues:
                print("Issues:")
                any_issues = True
            print(f"\n  {sr['name']} ({sr['email']})")
            for week, errors in issues:
                print(f"    Week {week}:")
                for err in errors:
                    print(f"      • {err}")

    if not any_issues:
        print("No issues found — all logs up to date.")


# ── Email notifications ───────────────────────────────────────────────────────

EMAIL_SUBJECT = "DREU Research Journal — Action Required"

EMAIL_BODY = """\
Hi {name},

This is an automated reminder from the DREU program about your research journal.

The following issues were found with your log at {repo_url}:

{issue_list}

Please address these as soon as possible. Each week's log is due by Sunday at 11:59 PM.

If you have any questions, contact the DREU program staff at dreu_staff@cra.org.

— DREU Program
"""


def send_email(to_name: str, to_email: str, repo_url: str, issues: list[tuple],
               cfg: configparser.ConfigParser):
    """Send a notification email to one student."""
    issue_lines = []
    for week, errors in issues:
        issue_lines.append(f"  Week {week}:")
        for err in errors:
            issue_lines.append(f"    • {err}")
    issue_list = "\n".join(issue_lines)

    body = EMAIL_BODY.format(
        name=to_name,
        repo_url=repo_url,
        issue_list=issue_list,
    )

    msg = EmailMessage()
    msg["Subject"] = EMAIL_SUBJECT
    msg["From"]    = cfg.get("smtp", "sender")
    msg["To"]      = to_email
    msg.set_content(body)

    host     = cfg.get("smtp", "host")
    port     = cfg.getint("smtp", "port")
    username = cfg.get("smtp", "username")
    password = cfg.get("smtp", "password")

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(msg)

    print(f"  Email sent to {to_name} <{to_email}>")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Check all DREU student logs.")
    parser.add_argument("--send-email", action="store_true",
                        help="Email students with missing or invalid logs")
    parser.add_argument("--week", type=int, default=None,
                        help="Override current week number (default: calculated from start_date)")
    args = parser.parse_args()

    cfg = load_config()

    # Determine current week
    if args.week:
        weeks_due = args.week
    else:
        start_date = date.fromisoformat(cfg.get("program", "start_date"))
        weeks_due  = current_week_number(start_date)
        if weeks_due == 0:
            print("Program has not started yet.")
            sys.exit(0)

    print(f"Checking logs for weeks 1–{weeks_due} ...")

    github_token = cfg.get("github", "token", fallback="")

    # Read students
    if not STUDENTS_FILE.exists():
        print(f"Error: {STUDENTS_FILE} not found.")
        sys.exit(1)

    with open(STUDENTS_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        students = list(reader)

    if not students:
        print("No students found in students.csv.")
        sys.exit(0)

    # Check each student
    students_results = []
    for s in students:
        name     = s["name"].strip()
        email    = s["email"].strip()
        doc_url  = s["repo_url"].strip()   # column holds either a GitHub or Google Docs URL
        doc_type = "Google Doc" if is_gdoc_url(doc_url) else "GitHub"
        print(f"  Checking {name} ({doc_type}) ...")

        if is_gdoc_url(doc_url):
            results = check_student_gdoc(name, doc_url, weeks_due)
        else:
            results = check_student(name, doc_url, weeks_due, token=github_token)

        students_results.append({
            "name":     name,
            "email":    email,
            "repo_url": doc_url,
            "results":  results,
        })

    print_report(students_results, weeks_due)

    # Send emails
    if args.send_email:
        print("\nSending email notifications ...")
        for sr in students_results:
            issues = [(r["week"], r["errors"]) for r in sr["results"] if r["errors"]]
            if issues:
                send_email(sr["name"], sr["email"], sr["repo_url"], issues, cfg)
        print("Done.")


if __name__ == "__main__":
    main()
