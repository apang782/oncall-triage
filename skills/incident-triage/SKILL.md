---
name: incident-triage
description: Read-only first-pass incident triage for a live Kubernetes service outage—metrics, error logs, correlation, handoff. Use when the user is on call, investigating elevated 5xx/latency/crash loop, or invokes /oncall-triage:incident-triage.
---

# Incident triage (read-only)

For the **primary on-call engineer** during a **live Kubernetes HTTP service incident** (first 15–30 minutes). Pair with the `triage` agent when the run needs many tool calls.

## Observability MCP (capability-based)

Use your plugin’s configured **read-only observability** MCP server—not browser tabs.

| Step | Capability | What to call |
|------|------------|--------------|
| 1 | **Cluster / metrics overview** | One-shot health: nodes, pod phases, restarts, saturation signals (CPU/memory/DB host if exposed) |
| 2 | **Error log search** | Query by severity, time window, optional text filter; prefer grouped signatures over raw duplicates |

**Rules:**

- Prefer these MCP capabilities over Grafana/Dashboards or browser automation.
- Discover the actual tool names from the MCP server Claude exposes (names vary by server).
- If no suitable read-only overview or log-search tools are available, stop and tell the user to fix plugin MCP config (`claude --plugin-dir …`, `/reload-plugins`)—do not improvise with browsers unless they ask.

Concrete tool names for **this** plugin’s demo server are documented in the README (**Tool mapping**)—not in this skill, so you can swap MCP backends without rewriting the playbook.

## Inputs

Collect anything missing before step 1:

| Field | Example |
|-------|---------|
| Cluster / env short name | `prod-acme` |
| Namespace (if not default) | `prod-acme` |
| Symptom | elevated 5xx, lag, crash loop |
| Time window | last 30m, since deploy at 14:00 UTC |

## 1. Metrics snapshot

Call the **cluster / metrics overview** tool (cluster short name + namespace if needed).

**Before moving on:**

- Pod counts **zero**? → verify env/cluster prefix; zero often means wrong query, not a healthy cluster.
- Note Pending / CrashLoop pods and top restart offenders.
- If the response includes managed database / Postgres host metrics, note host CPU vs connection saturation.

## 2. Error logs

Call the **log search** tool with:

- `severity`: `ERROR` first, then `WARN` if sparse
- `query`: symptom keywords or `*`
- `time_range` (or your server’s equivalent string param)—**not** legacy `hours=` unless the tool schema defines it

**Before moving on:**

- **`unknown_args_warning` (or similar) present?** → fix arguments before interpreting results.
- Echo **`effective_lookback`** (or equivalent); do not assume the window you intended was applied.
- Group stacks by **signature**; report counts.

## 3. Correlate

**Facts** — only what metrics and logs show (counts, signatures, timestamps).

**Hypotheses** — up to 3, each with **high / medium / low** confidence and the fact(s) that support it. Do not state hypotheses as facts.

## 4. Handoff

1. **Safe next steps** — read-only only (`kubectl get` / `describe` / `logs`, links, page owners).
2. **Needs human approval** — writes, deletes, rollbacks, scale, pool changes, or tickets filed on hypothesis alone.

If the MCP response indicates demo/mock data, say so and point the user to the plugin README for production MCP setup.

## 5. Stop

Escalate to a human when:

- User needs production data and observability MCP is not configured for their environment.
- Auth failures persist after credential check.
- Evidence suggests security incident (exfil, credential leak).
