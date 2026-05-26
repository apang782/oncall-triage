---
name: incident-triage
description: Read-only first-pass incident triage for a live Kubernetes service outage—metrics, error logs, correlation, handoff. Use when the user is on call, investigating elevated 5xx/latency/crash loop, or invokes /oncall-triage:incident-triage.
---

## MCP

- Use read-only observability tools from the loaded plugin; call only MCP tool names exposed in this session (e.g. `mcp__<server>__<tool>`)—do not invent names.
- If cluster overview or log-search tools are unavailable: stop and tell the user to fix `.mcp.json` / `claude --plugin-dir` / `/reload-plugins` (plugin README). Do not open Dashboards or drive a browser unless user explicitly asks.

## Inputs

Ask the user for anything missing before proceeding:


| Field                      | Example                             |
| -------------------------- | ----------------------------------- |
| Cluster / env short name   | `prod-acme`                         |
| Namespace (if not default) | `prod-acme`                         |
| Symptom                    | elevated 5xx, lag, crash loop       |
| Time window                | last 30m, since deploy at 14:00 UTC |


## 1. Metrics snapshot

Call the cluster / metrics overview tool (cluster short name + namespace if needed). Prefer read-only MCP tools over browser or Dashboards.

**Before moving on:**

- Pod counts zero? → verify env/cluster prefix; zero often means wrong query, not a healthy cluster.
- Note Pending / CrashLoop pods and top restart offenders.
- If the response includes managed database host metrics, note host CPU vs connection saturation.

## 2. Error logs

Call the log search tool with:

- `severity`: `ERROR` first, then `WARN` if sparse
- `query`: symptom keywords or `*`
- `time_range` string param (e.g. `"30m"`)—not legacy `hours=`

**Before moving on:**

- `unknown_args_warning` present? → fix arguments before interpreting results.
- Echo `effective_lookback`; do not assume the window you intended was applied.
- Group stacks by signature; report counts.

## 3. Correlate

**Facts** — only what metrics and logs show (counts, signatures, timestamps).

**Hypotheses** — up to 3, each with high / medium / low confidence and the fact(s) that support it. Do not state hypotheses as facts.

## 4. Handoff

1. **Safe next steps** — read-only only (`kubectl get` / `describe` / `logs`, links, page owners).
2. **Needs human approval** — writes, deletes, rollbacks, scale, pool changes, or tickets filed on hypothesis alone.

If the MCP response indicates demo/mock data, say so and point the user to the plugin README for production MCP setup.

## 5. Stop

Escalate to a human when:

- User needs production data and observability MCP is not configured for their environment.
- Auth failures persist after credential check.
- Evidence suggests security incident (exfil, credential leak).

