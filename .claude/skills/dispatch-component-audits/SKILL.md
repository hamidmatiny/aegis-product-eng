---
name: dispatch-component-audits
description: Manager-triggered component audits. Each hourly run (08:00-12:00 UTC) dispatches exactly one of the five component owners over A2A, so the audits are staggered instead of a burst. Use for the scheduled dispatch or when asked to kick off a component audit.
user-invocable: true
---

# Dispatch component audits

ICs (`aegis-gateway`, `aegis-policy-engine`, `aegis-model-router`, `aegis-agent-gate`, `aegis-audit`) have no cron of their own. Their manager triggers them over the standing A2A edges (Hamid's hierarchy rule). One IC per run, one hour apart.

## Steps

1. Run `python3 scripts/next_ic.py`. It prints the IC for this UTC hour (`dispatch`, `component`, `message`). If it exits 1 (outside 08-12 UTC) and nobody named an IC explicitly, dispatch nobody and say so in the close-out.
2. Send `message` to `dispatch` with `mcp__trinity__chat_with_agent`. Do not wait for the audit to finish if the tool offers async/parallel mode; the IC runs as its own execution and posts its own close-out. Record whether the dispatch call itself was accepted (the tool's response), never assume it.
3. Check the IC dispatched in the previous slot (if any): read its latest execution with `mcp__trinity__list_recent_executions` (or the closest available tool) and note `status` and whether it posted a Slack close-out. Report what you saw; do not grade from memory.
4. Append one line to `memory/dispatch-log.md`: UTC time, IC, component, dispatch response, previous IC's result.
5. Slack close-out to `#aegis-product-eng` (HARD GATE): who was dispatched, whether the call was accepted, the previous IC's result.

Never dispatch more than one IC per run. Never change an IC's schedules.
