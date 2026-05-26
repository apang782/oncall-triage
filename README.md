# oncall-triage

Claude Code plugin for the engineer **holding the pager** during a **live incident on a Kubernetes-backed HTTP service**—structured, **read-only** first-pass triage (metrics → logs → correlation) with observability MCP tools, a playbook skill, and Bash safety hooks.

**Persona:** Primary on-call engineer responding to a production incident (e.g. elevated 5xx, latency spike, or crash loop on one cluster/namespace)—not someone doing Terraform rollouts, capacity planning, or postmortem writing.

**Problem:** In the first 15–30 minutes of an incident, triage is ad-hoc Grafana tabs and log queries; an AI assistant may suggest destructive `kubectl` or apply commands before blast radius is understood.

**Solution:** `/oncall-triage:incident-triage` skill + `triage` agent + mock read-only MCP + PreToolUse hook. The plugin does not remediate the outage—it structures investigation and blocks dangerous shell.

**Out of scope:**

- Deploying or changing infrastructure (scale, restart, delete, rollback)
- CVE triage, data pipelines, or application feature debugging outside service health
- Replacing your org’s observability stack (use mock MCP for demo; swap `.mcp.json` for real read-only servers in production)

---

## Install (under 5 minutes)

**Prerequisites:** [Claude Code](https://code.claude.com/) CLI, **Python 3.10+**.

```bash
git clone https://github.com/apang782/oncall-triage oncall-triage-plugin
cd oncall-triage-plugin
pip install -r mcp-servers/mock-observability/requirements.txt
claude plugin validate .
```

### Run the plugin (local — what graders clone)

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

| Component | Path | Role |
|-----------|------|------|
| Agent `triage` | `agents/triage.md` | Read-only investigation workflow |
| Skill `/oncall-triage:incident-triage` | `skills/incident-triage/SKILL.md` | Playbook + silent-failure checks |
| MCP `mock-observability` | `.mcp.json` + `mcp-servers/` | Canned logs/metrics for workshops |
| Hook | `hooks/hooks.json` + `scripts/pre_tool_guard.py` | Blocks destructive Bash |

---

## Design: portable skill, plugin-specific wiring

The **skill** describes an MCP-agnostic triage procedure (overview → logs → correlate → handoff). It intentionally does **not** hard-code tool names, so teams can swap observability backends without rewriting the playbook.

**Plugin-specific names** live here and in `agents/triage.md`:

| Capability | This repo (demo) | You fork for production |
|------------|------------------|-------------------------|
| MCP server | `mock-observability` | Your server key in `.mcp.json` (e.g. `opensearch-logs`, `grafana-metrics`) |
| Cluster / metrics overview | `cluster_overview` | Your read-only macro or instant query tool |
| Error log search | `search_logs` | Your read-only log query tool |
| Claude may expose as | `mcp__mock-observability__cluster_overview`, etc. | `mcp__<your-server>__<tool>` |

**What to edit when swapping MCP:**

1. **`.mcp.json`** — point at your read-only server(s).
2. **`agents/triage.md`** — update server id and tool names in **Tool priority** and workflow steps.
3. **`skills/incident-triage/SKILL.md`** — usually **unchanged** (capability-based); only edit if your runbook adds org-specific steps (PagerDuty, escalation).

---

## Swap mock → production MCP

Edit `.mcp.json` to point at your org's read-only servers (no writes on the tool surface):

```json
{
  "mcpServers": {
    "opensearch-logs": { "command": "...", "args": ["..."] },
    "grafana-metrics": { "command": "...", "args": ["..."] }
  }
}
```

Update **`agents/triage.md`** tool names to match your server (see **Tool mapping** above). The **skill** stays capability-based; silent-failure guards in the skill apply to any backend that returns similar fields.

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

Production read-only OpenSearch/Grafana MCPs (replacing the mock), a docker-compose workshop lab, and CI running `claude plugin validate`. Same split: ship read-only triage producers first; gate automated playbooks or ticket writers until cost and loop controls exist. I'd also verify delegated triage subagent tool inheritance and add a tested read-only tools allowlist once MCP access on spawn is confirmed.

---

## License

MIT
