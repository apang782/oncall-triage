# oncall-triage

Claude Code plugin for **platform / SRE engineers** on call: structured, **read-only** incident triage using observability MCP tools, a playbook skill, and Bash safety hooks.

**Persona:** Platform engineer investigating production degradation (Kubernetes + logs + metrics).

**Problem:** Ad-hoc Dashboards + PromQL is slow, brittle, and risky when an agent can run destructive shell commands.

**Solution:** `/incident-triage` skill + `triage` agent + mock read-only MCP + PreToolUse hook.

---

## Install (under 5 minutes)

**Prerequisites:** [Claude Code](https://code.claude.com/) CLI, **Python 3.10+**.

```bash
git clone <your-repo-url> oncall-triage-plugin
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
4. Ask Claude to use the **triage** agent or MCP tools `cluster_overview` and `search_logs` on `mock-observability`.
5. **Hook demo:** ask Claude to run `kubectl delete pod foo` in Bash — the hook should block with an oncall-triage message.

---

## What's in the box

| Component | Path | Role |
|-----------|------|------|
| Agent `triage` | `agents/triage.md` | Read-only investigation workflow |
| Skill `/incident-triage` | `skills/incident-triage/SKILL.md` | Playbook + silent-failure checks |
| MCP `mock-observability` | `.mcp.json` + `mcp-servers/` | Canned logs/metrics for workshops |
| Hook | `hooks/hooks.json` + `scripts/pre_tool_guard.py` | Blocks destructive Bash |

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

Update `agents/triage.md` tool names to match your server's registered tools. Keep the skill's silent-failure checks—they apply to any backend.

---

## Validate (automated, no API)

```bash
# Windows
powershell -File scripts/smoke-test.ps1

# Or manually
claude plugin validate . --strict
```

---

## With more time (scoping note for submission)

I'd replace the mock MCP with production-hardened read-only log and metrics servers (strict arg validation, series limits, auth error surfacing), add a workshop docker-compose lab, and ship CI that runs `claude plugin validate` on every PR.

---

## License

MIT
