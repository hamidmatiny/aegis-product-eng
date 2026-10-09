#!/usr/bin/env python3
"""Which component owner this manager run dispatches. No model involved.

The manager's schedule fires hourly 08:00-12:00 UTC; each run dispatches one IC,
so the five component audits are an hour apart instead of a burst on the shared
OmniRoute pool. ICs have no cron of their own: the manager triggers them over its
A2A edges (Hamid's hierarchy rule).

  python3 scripts/next_ic.py            # JSON for the current UTC hour
  python3 scripts/next_ic.py --hour 9
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

FIRST_HOUR = 8
ROTATION = (
    ("aegis-gateway", "gateway"),
    ("aegis-policy-engine", "policy-engine"),
    ("aegis-model-router", "model-router"),
    ("aegis-agent-gate", "agent-gate"),
    ("aegis-audit", "audit"),
)
CRON = f"0 {FIRST_HOUR}-{FIRST_HOUR + len(ROTATION) - 1} * * *"


def pick(hour: int) -> dict:
    slot = hour - FIRST_HOUR
    if not 0 <= slot < len(ROTATION):
        return {"dispatch": None, "reason": f"hour {hour:02d} UTC is outside the {CRON} slots"}
    agent, component = ROTATION[slot]
    return {
        "dispatch": agent,
        "component": component,
        "slot": slot + 1,
        "of": len(ROTATION),
        "message": (
            f"Run /audit-component on `{component}`. Cite real files. Update memory/backlog.md with "
            "findings. If a fix is ready, prepare /open-component-pr; do not merge. Dispatched by "
            "aegis-product-eng (your manager). Post your own Slack close-out when done."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--hour", type=int)
    args = p.parse_args(argv)
    hour = args.hour if args.hour is not None else datetime.now(timezone.utc).hour
    out = pick(hour)
    print(json.dumps(out, indent=2))
    return 0 if out["dispatch"] else 1


if __name__ == "__main__":
    sys.exit(main())
