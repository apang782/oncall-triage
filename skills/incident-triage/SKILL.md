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

- Read `unknown_args_warning` if present—do not ignore silent arg drops.
- Group duplicate stack traces by signature; report occurrence counts.

### 3. Correlate and hypothesize

Produce:

1. **Facts** (metrics + logs only)
2. **Top 2–3 hypotheses** with confidence
3. **Safe next steps** (read-only kubectl, dashboard links, paging owners)
4. **Needs human approval** (writes, deletes, rollbacks)

### 4. Stop conditions

Stop and escalate to a human when:

- Data is mock/demo and user needs production truth → instruct them to swap `.mcp.json` for real servers (see plugin README).
- Auth failures persist after credential check.
- Evidence points to security incident (exfil, credential leak).

## Enterprise patterns (teaching notes)

- **Read-only by construction**: only query tools on the MCP surface.
- **Surface silent failures**: zero pods, unknown args, ambiguous time ranges.
- **MCP before browser**: programmatic triage preserves tokens and auditability.
