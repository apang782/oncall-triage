# Loom outline (≤5 min) — oncall-triage

Record in this order. Stumble OK; talk through it.

## 0:00–0:30 — Who + problem

- **Persona:** Platform / SRE engineer on call for Kubernetes-backed services.
- **Pain:** Triage = Dashboards + ad-hoc queries + risk of destructive shell; slow and hard to repeat across engineers.

## 0:30–2:00 — Live demo

1. `claude` in a repo with plugin installed.
2. `/oncall-triage:incident-triage` → give `prod-acme`, "elevated 5xx".
3. Show MCP `cluster_overview` + `search_logs` (grouped signatures; optional: `managed_postgres` CPU — non-obvious metric names bite in prod).
4. **Silent failure:** `search_logs` with `hours=1` → read `unknown_args_warning` aloud; retry with `time_range="1h"`.
5. Trigger hook: ask for `kubectl delete pod x` → show block message.
6. One sentence: "Swap `.mcp.json` for real read-only servers in production."

## 2:00–3:30 — How you built it + steering Claude

**Decision 1:** Read-only MCP surface (two query tools only)—safety in schema, not prompts. *(Bob: OpenSearch/Grafana MCP pattern)*

**Decision 2:** Skill encodes silent-failure checks (zero pods, `unknown_args_warning`, facts-before-hypotheses)—from agents misreading "healthy" when env prefix was wrong or args were silently dropped.

**Decision 3 (scoping):** Spec-first + producer/consumer—mock MCP and skill shipped; automated playbook generation explicitly gated.

**Steering Claude:** "Agent draft was too verbose; I disallowed Write/Edit and capped turns." / "Hook initially blocked all git push; I narrowed to main."

**Optional 10s color:** Production incident where wrong Prometheus metric name wasted hours—why `cluster_overview` encodes triage shape, not raw PromQL.

## 3:30–4:30 — Walk through customer guide

Open `BUILD_YOUR_OWN_PLUGIN.md`:

- Start with persona sentence, not JSON.
- Spec-first section — file tool surface before code when MCP is non-trivial.
- Copy skill → adapt runbook steps.
- Point `.mcp.json` at their servers.
- Extend hook deny list.

## 4:30–5:00 — With more time

Production read-only MCPs, compose lab, CI validate—and keep gating automated consumers until trust/cost controls exist.

---

## Submission blurb (paste into email/README)

Built **oncall-triage** for platform engineers on call: `/oncall-triage:incident-triage` skill, `triage` agent, mock read-only observability MCP (including `unknown_args_warning`), and PreToolUse Bash guard. Patterns from shipping read-only log/metrics MCPs in production agent platforms: MCP-before-browser, surface silent failures, facts-before-hypotheses, land producers before gated consumers. With more time: production MCP backends, compose lab, CI validation.
