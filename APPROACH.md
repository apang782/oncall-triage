# Tier A approach (your checklist)

## Persona

**Platform / SRE engineer on call** — Kubernetes + OpenSearch/logs + Grafana/metrics.

## Bob patterns used (interview stories, not in README verbatim)

| Bob lesson | Plugin artifact |
|------------|-----------------|
| MCP before browser | `agents/triage.md` tool priority |
| Read-only tool surface | mock MCP: only `search_logs`, `cluster_overview` |
| Silent failure checks | `skills/incident-triage/SKILL.md` |
| Main-push / destructive guard | `scripts/pre_tool_guard.py` |
| Grouped log signatures | mock `search_logs` response shape |

## 3-hour time budget

| Done (~now) | You still do |
|-------------|--------------|
| Plugin scaffold | `claude plugin validate .` on your machine |
| README + customer guide | Record Loom (`LOOM_OUTLINE.md`) |
| Loom script | Public GitHub repo + author name in manifest |
| | Human pass on agent/skill prose (anti-slop edit) |

## Submit

1. Repo: `oncall-triage-plugin/`
2. Guide: `BUILD_YOUR_OWN_PLUGIN.md`
3. Loom: follow `LOOM_OUTLINE.md`
