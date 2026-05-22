# Loom outline (≤5 min) — oncall-triage

Record in this order. Stumble OK; talk through it.

## 0:00–0:30 — Who + problem

- **Persona:** Platform / SRE engineer on call for Kubernetes-backed services.
- **Pain:** Triage = Dashboards + ad-hoc queries + risk of destructive shell; slow and hard to repeat across engineers.

## 0:30–2:00 — Live demo

1. `claude` in a repo with plugin installed.
2. `/oncall-triage:incident-triage` → give `prod-acme`, "elevated 5xx".
3. Show MCP `cluster_overview` + `search_logs` returning mock grouped data.
4. Trigger hook: ask for `kubectl delete pod x` → show block message.
5. One sentence: "Swap `.mcp.json` for real read-only servers in production."

## 2:00–3:30 — How you built it + steering Claude

**Decision 1:** Read-only MCP surface (two query tools only)—safety in schema, not prompts. *(Bob: OpenSearch/Grafana MCP pattern)*

**Decision 2:** Skill encodes silent-failure checks (zero pods, unknown args)—from seeing agents misread "healthy" when env prefix was wrong.

**Steering Claude:** "Agent draft was too verbose; I disallowed Write/Edit and capped turns." / "Hook initially blocked all git push; I narrowed to main."

## 3:30–4:30 — Walk through customer guide

Open `BUILD_YOUR_OWN_PLUGIN.md`:

- Start with persona sentence, not JSON.
- Copy skill → adapt runbook steps.
- Point `.mcp.json` at their servers.
- Extend hook deny list.

## 4:30–5:00 — With more time

Real read-only MCP servers, docker-compose lab, CI validate on PR.

---

## Submission blurb (paste into email/README)

Built **oncall-triage** for platform engineers on call: `/incident-triage` skill, `triage` agent, mock read-only observability MCP, and PreToolUse Bash guard. Patterns drawn from shipping similar read-only log/metrics MCP tooling in production agent platforms (routing MCP before browser, surfacing silent failures). With more time: production MCP backends, compose lab, and CI validation.
