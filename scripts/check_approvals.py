#!/usr/bin/env python3
"""Lint text for uncited approval claims (CLAUDE.md HARD GATE). No model involved.

Every sentence that says something was approved / authorized / signed off / cleared,
or that a PR is pending / open / merged, must cite in the same sentence either a PR
URL (https://github.com/hamidmatiny/<repo>/pull/<n>) or a responded operator-queue
item (`request_id` ... `responded`). Negated true-state phrasing ("not approved",
"no PR opened") is allowed.

  python3 scripts/check_approvals.py closeout.txt
  echo "PR merged." | python3 scripts/check_approvals.py -

Exit 0 = clean, 1 = uncited claims (printed as JSON), 2 = usage error.
"""

from __future__ import annotations

import json
import re
import sys

CLAIM = re.compile(
    r"\b(approved|approval granted|authori[sz]ed|signed[- ]off|sign-?off given|cleared"
    r"|PRs?\b[^.!?\n]{0,40}?\b(?:pending|open|opened|merged))\b",
    re.IGNORECASE,
)
NEGATION = re.compile(r"\b(not|no|never|un|without|nothing)\b[\s\w`'-]{0,25}$", re.IGNORECASE)
PR_URL = re.compile(r"https://github\.com/hamidmatiny/[\w.-]+/pull/\d+")
QUEUE = re.compile(r"request_id\W+[\w-]+", re.IGNORECASE)
SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")


def cited(sentence: str) -> bool:
    if PR_URL.search(sentence):
        return True
    return bool(QUEUE.search(sentence)) and "responded" in sentence.lower()


def negated(sentence: str, start: int) -> bool:
    return bool(NEGATION.search(sentence[:start]))


def find_uncited(text: str) -> list[dict]:
    problems = []
    for sentence in SENTENCE.split(text):
        sentence = sentence.strip()
        if not sentence or cited(sentence):
            continue
        for m in CLAIM.finditer(sentence):
            if not negated(sentence, m.start()):
                problems.append({"claim": m.group(0), "sentence": sentence})
                break
    return problems


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    text = sys.stdin.read() if argv[0] == "-" else open(argv[0], encoding="utf-8").read()
    problems = find_uncited(text)
    print(json.dumps({"ok": not problems, "uncited": problems}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
