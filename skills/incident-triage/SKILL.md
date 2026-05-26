---
name: incident-triage
description: Run a structured read-only incident triage—metrics overview, error logs, silent-failure checks, and a handoff summary. Use when the user says they are on call, investigating an outage, or invokes /oncall-triage:incident-triage.
---

# Incident triage (read-only)

Use this skill for **platform / SRE on-call** investigating production degradation. Pair with the `triage` agent when the investigation spans multiple tool calls.

## Inputs to collect first

Ask the user for anything missing:

| Field | Example |
|-------|---------|
| Cluster / env short name | `prod-acme` |
| Namespace (if not default) | `prod-acme` |
| Symptom | elevated 5xx, lag, crash loop |
| Time window | last 30m, since deploy at 14:00 UTC |

## Steps

### 1. Metrics snapshot

Invoke MCP tool `cluster_overview` with the cluster short name.

**Check before moving on:**

- Are pod counts zero? → verify cluster/env naming; zero often means wrong prefix, not empty cluster.
- Any Pending or CrashLoop pods? Note top restart offenders.
- If `managed_postgres` is present, note host CPU vs connection saturation.

### 2. Error logs

Invoke MCP tool `search_logs` with:

- `severity`: `ERROR` first, then `WARN` if sparse
- `query`: user symptom keywords or `*` if unknown
- `time_range`: `30m` unless user specified otherwise

**Check:**

- If the response includes **`unknown_args_warning`**, stop and fix tool arguments before continuing. (Demo: passing `hours=1` instead of `time_range="1h"` triggers this—older servers silently fell back to a 1h default with no signal.)
- Group duplicate stack traces by signature; report occurrence counts.
- Echo **`effective_lookback`** (or equivalent) from the response; do not assume the window you intended was applied.

### 3. Correlate — facts before hypotheses

Separate evidence from inference (partial reads and wrong env prefixes have caused bad escalations):

1. **Facts** — only what metrics and logs explicitly show (counts, signatures, timestamps).
2. **Hypotheses** — 2–3 items, each with **high / medium / low** confidence and which fact supports it.
3. **Safe next steps** — read-only checks only (kubectl get/describe/logs, links, page owners).
4. **Needs human approval** — any write, delete, rollback, scale, or ticket filed on hypothesis alone.

Do not recommend destructive actions or definitive root cause without fact backing.

### 4. Stop conditions

Stop and escalate to a human when:

- Data is mock/demo and user needs production truth → instruct them to swap `.mcp.json` for real servers (see plugin README).
- Auth failures persist after credential check.
- Evidence points to security incident (exfil, credential leak).

## Enterprise patterns (teaching notes)

- **Read-only by construction**: only query tools on the MCP surface.
- **Surface silent failures**: zero pods, unknown args, ambiguous time ranges.
- **MCP before browser**: programmatic triage preserves tokens and auditability.
