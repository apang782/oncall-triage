#!/usr/bin/env python3
"""
PreToolUse guard for Bash: block destructive on-call footguns.
Exit 0 = allow, 1 = allow with warning (stdout), 2 = deny.
"""
from __future__ import annotations

import json
import re
import sys

BLOCK_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bkubectl\s+(delete|drain|cordon)\b", re.I), "kubectl destructive subcommand"),
    (re.compile(r"\bterraform\s+apply\b", re.I), "terraform apply"),
    (re.compile(r"\bgit\s+push\b.*\bmain\b", re.I), "git push to main"),
    (re.compile(r"\bgit\s+push\s+-u\s+origin\s+main\b", re.I), "git push -u origin main"),
    (re.compile(r"\bcurl\b.*\s(-X\s+POST|-d\b).*--delete", re.I), "suspicious curl mutation"),
]


def main() -> None:
    raw = sys.stdin.read()
    command = ""
    try:
        payload = json.loads(raw) if raw.strip() else {}
        tool_input = payload.get("tool_input") or payload.get("input") or {}
        if isinstance(tool_input, dict):
            command = tool_input.get("command") or tool_input.get("cmd") or ""
        if not command and isinstance(payload.get("command"), str):
            command = payload["command"]
    except json.JSONDecodeError:
        command = raw

    for pattern, label in BLOCK_PATTERNS:
        if pattern.search(command):
            msg = (
                f"[oncall-triage] Blocked Bash: {label}. "
                "Destructive changes require explicit human approval outside this plugin."
            )
            print(msg, file=sys.stderr)
            sys.exit(2)

    if re.search(r"\bkubectl\s+apply\b", command, re.I):
        print(
            "[oncall-triage] Warning: kubectl apply detected—confirm change ticket and blast radius.",
            file=sys.stderr,
        )
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
