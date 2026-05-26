# oncall-triage

Claude Code plugin for the engineer **holding the pager** during a **live incident on a Kubernetes-backed HTTP service**—structured, **read-only** first-pass triage (metrics → logs → correlation) with observability MCP tools, a playbook skill, and Bash safety hooks.

**Persona:** Primary on-call engineer responding to a production incident (e.g. elevated 5xx, latency spike, or crash loop on one cluster/namespace)—not someone doing Terraform rollouts, capacity planning, or postmortem writing.

**Problem:** In the first 15–30 minutes of an incident, triage is ad-hoc Grafana tabs and log queries; an AI assistant may suggest destructive `kubectl` or apply commands before blast radius is understood.

**Solution:** `/oncall-triage:incident-triage` skill + `triage` agent + PreToolUse hook (mock MCP bundled for demo installs only). Does not remediate the outage—structures read-only first-pass triage and blocks dangerous shell when wired to your observability MCPs.

**Out of scope:**

- Deploying or changing infrastructure (scale, restart, delete, rollback)
- CVE triage, data pipelines, or application feature debugging outside service health
- Replacing your org’s observability stack (demo uses a **mock** MCP; production means **wiring this plugin to MCP servers you already run**)

---

## Install (under 5 minutes)

**Prerequisites:** [Claude Code](https://code.claude.com/) CLI, **Python 3.10+**.

```bash
git clone https://github.com/apang782/oncall-triage oncall-triage-plugin
cd oncall-triage-plugin
pip install -r mcp-servers/mock-observability/requirements.txt
claude plugin validate .
```

### Run the plugin (local install)

`claude plugin install` is for marketplace plugins. For a local repo, use `--plugin-dir`:

```bash
cd oncall-triage-plugin
pip install -r mcp-servers/mock-observability/requirements.txt
claude plugin validate .

# From any project directory:
claude --plugin-dir c:/path/to/oncall-triage-plugin
```

Plugin skills are **namespaced**: `/oncall-triage:incident-triage` (not `/incident-triage`).

Reload after edits: `/reload-plugins`

---

## Try it (demo script)

1. Start Claude Code in any repo: `claude`
2. Run the skill: `/oncall-triage:incident-triage`
3. When prompted, use demo inputs:
   - Cluster: `prod-acme`
   - Symptom: elevated 5xx since last deploy
4. Ask Claude to use MCP tools `cluster_overview` and `search_logs` on `mock-observability`.
5. **Silent-failure demo:** call `search_logs` with `hours=1` (wrong param) — response should include `unknown_args_warning`; use `time_range="1h"` instead.
6. **Hook demo:** ask Claude to run `kubectl delete pod foo` in Bash — the hook blocks the command string before it runs (no real cluster required).

---

## What's in the box

Use the **skill** in the main session for a guided pass; delegate to the **`triage` agent** for longer multi-tool runs.

| Component | Path | Role |
|-----------|------|------|
| Agent `triage` | `agents/triage.md` | Read-only investigation workflow (concrete MCP tool names) |
| Skill `/oncall-triage:incident-triage` | `skills/incident-triage/SKILL.md` | Portable playbook + silent-failure checks (capability-based) |
| MCP `mock-observability` | `.mcp.json` + `mcp-servers/` | Canned logs/metrics for workshops |
| Hook | `hooks/hooks.json` + `scripts/pre_tool_guard.py` | Blocks destructive Bash |

---

## Wire your observability MCPs (production)

This plugin ships a **triage workflow** (skill, agent, hook)—not a new Grafana or OpenSearch stack. The **`mock-observability`** server is for workshops only; in production you register **MCP servers you already run**.

The **skill** is capability-based (overview → logs → correlate → handoff) and usually stays unchanged. **Tool names** are wired in `agents/triage.md` and `.mcp.json`:

| Capability | This repo (demo) | Your environment |
|------------|------------------|------------------|
| MCP server | `mock-observability` | Your key(s) in `.mcp.json` |
| Cluster / metrics overview | `cluster_overview` | Your read-only overview tool |
| Error log search | `search_logs` | Your read-only log query tool |
| In Claude | `mcp__mock-observability__…` | `mcp__<your-server>__<tool>` |

**Steps:** (1) Confirm you have read-only overview + log-search MCP tools (if you only have Dashboards UI, add MCP for those systems first). (2) Point `.mcp.json` at your server commands/creds—example:

```json
{
  "mcpServers": {
    "your-log-mcp": { "command": "...", "args": ["..."] },
    "your-metrics-mcp": { "command": "...", "args": ["..."] }
  }
}
```

(3) Update `agents/triage.md` with your server keys and tool names. (4) Keep the skill unless you add org runbook steps (PagerDuty, escalation).

---

## Validate (automated, no API)

```bash
# Windows
powershell -File scripts/smoke-test.ps1

# Or manually
claude plugin validate .
```

---

## With more time

Optional **reference** read-only OpenSearch/Grafana MCP implementations (for teams that do not already have log/metrics MCPs)—not required for adoption if you bring your own servers. Plus a docker-compose workshop lab, CI `plugin validate`, verified subagent tool inheritance, and a tested read-only tool allowlist on spawn.

---

## License

MIT
