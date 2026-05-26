# Build your own Claude Code plugin

A [Claude Code plugin](https://code.claude.com/docs/en/plugins) bundles an AI workflow — a repeatable checklist, a specialist agent, live data tools, and safety guardrails — so your whole team runs the same procedure and enforces the same guardrails, rather than each engineer prompting from scratch.

**Fast path:** start with **skill + agent**. Most workflows start there — add MCP when you need live data from an external system, hooks when you need a guardrail that can't be bypassed.

---

## 1. Start with persona + pain (not `plugin.json`)

Write one sentence before touching any files:

> *Who* is stuck, *what* are they doing, *what breaks today*?

This guide uses the oncall-triage plugin as the worked example throughout. The same pattern applies to any workflow — here's how you'd frame this repo's workflow alongside a hypothetical one for your team:

| Field | This repo (oncall-triage) | Your workflow (example) |
|-------|--------------------------|------------------------|
| **Who** | On-call platform engineer responding to a live Kubernetes incident | Senior engineers doing code review |
| **What** | Triage via ad-hoc Grafana tabs and log queries under time pressure | Manually checking diffs for security anti-patterns |
| **Breaks today** | Slow and inconsistent; no guardrails against an AI suggesting destructive commands mid-investigation | Takes an hour per review; juniors miss patterns seniors catch by instinct |
| **Plugin** | `/oncall-triage:incident-triage` — structured read-only triage with a Bash guard | `/security-review` — runs your org's anti-pattern checklist against the diff before merge |

Start with one job. It's easier to expand a focused plugin than to untangle a broad one.

---

## 2. Pick your components

| Piece | When you need it | Why |
|-------|------------------|-----|
| [**Skill**](https://code.claude.com/docs/en/skills) (`skills/<name>/SKILL.md`) | Repeatable checklist Claude or the user invokes (`/your-skill`) | Encodes the procedure once; every engineer gets the same steps |
| [**Agent**](https://code.claude.com/docs/en/agents) (`agents/<name>.md`) | Multi-step work that spans many tool calls | Isolates context so the parent session stays clean |
| [**MCP**](https://code.claude.com/docs/en/mcp) (`.mcp.json`) | Live data from external systems: logs, metrics, tickets, CMDB | Programmatic access beats browser-driving for speed, tokens, and auditability |
| [**Hook**](https://code.claude.com/docs/en/hooks-guide) (`hooks/hooks.json`) | Hard guardrails: block deletes, warn on `apply`, audit egress | Hooks enforce; prompts only suggest — users can ignore a prompt, not a hook |

Ship **skill + agent + (MCP or hook)**. Don't bolt on components to check boxes.

### Skill vs agent — keep them separate

| Artifact | Put here | Not here | Why |
|----------|----------|----------|-----|
| **Skill** | Procedure: inputs, step order, guards | Vendor-specific MCP tool names | Tool names change when you swap backends; procedure shouldn't have to |
| **Agent** | Tool priority + your server/tool names | A second copy of the whole playbook | Duplicating the workflow means updating two files every time the procedure changes |
| **README** | Tool mapping table: capability → server → tool | Business logic | Humans need the mapping; the model gets it from the agent |

### Standard layout

```text
my-plugin/
├── .claude-plugin/plugin.json   # name required
├── skills/my-workflow/SKILL.md
├── agents/specialist.md
├── hooks/hooks.json             # optional
├── .mcp.json                    # optional
└── README.md
```

---

## 3. Build order

1. **Skill first** — inputs, ordered steps, stop conditions. Test immediately: `/my-skill`.
2. **Agent second** — wire tool priority ("MCP before Bash") and your server/tool names.
3. **MCP or hook last** — only when the skill can't be honest without live data or a hard block.

Validate as you go: `claude plugin validate ./my-plugin`

When MCP or hook design is non-trivial, write a one-page spec first: what tools you'll expose, what they won't do, open questions. Implement after you have answers.

---

## 4. When to use what

```text
Need live data from a system?      → MCP (read-only tools first)
Need to block dangerous commands?  → PreToolUse hook (exit 2 = deny)
Just need consistent procedure?    → Skill only
Long investigation eating context? → Agent
```

**Safety rule:** read-only by construction (no write tools on the MCP surface) beats "please don't delete" in a prompt.

---

## 5. Design decisions in this plugin

| Decision | Where | Why |
|----------|-------|-----|
| MCP before browser | `agents/triage.md` tool priority | Programmatic tools are faster, cheaper in tokens, and auditable |
| Concrete tool mapping in agent + README | `agents/triage.md`, README | Agent needs exact names; skill stays portable |
| Silent-failure guards | skill steps 1–2 | Zero pods ≠ healthy; wrong args silently defaulted — baked into procedure |
| Mock MCP | `mcp-servers/mock-observability/` | Demo and workshops run without prod credentials |
| Defence in depth | skill (procedure) + hook (Bash deny list) | Two independent layers — bypassing one doesn't bypass the other |

**If your workflow overlaps with this one** (observability triage on a different stack), fork directly:

1. Copy `skills/incident-triage/SKILL.md` → edit runbook/escalation steps; keep capability-based.
2. Copy `agents/triage.md` → set your MCP server id and tool names.
3. Update `.mcp.json` → your read-only server(s), no write tools.
4. Add a tool-mapping table to your README.
5. Extend `scripts/pre_tool_guard.py` with your banned commands (`aws s3 rm`, `helm uninstall`, etc.).

For any other workflow, the pattern in sections 1–4 is your starting point — not this fork list.

---

## 6. Tradeoff: portable skill vs explicit wiring

This repo uses what we'll call the **portable-skill / explicit-agent split**: the skill names capabilities ("cluster/metrics overview", "log search"), while the agent wires concrete tool names like `cluster_overview` on `mock-observability`. Teams swap the MCP backend by editing the agent and config — the skill never changes.

You could go fully portable (capabilities everywhere) or fully explicit (tool names everywhere). The split lets you take both wins:

- **Skill stays portable**: stable across teams; smaller token footprint; fewer forks when tool names differ.
- **Agent stays explicit**: reliable invocation of the exact MCP tools available in a given environment.

**Cost of the split:** the workflow exists in both files, so procedure updates touch two places. Acceptable for small plugins; at scale, generate one from the other or pick a single canonical entry point.

---

## 7. Testing checklist

Run on a fresh clone (or a teammate's machine) before declaring the plugin done — catches the gap between "works on mine" and "works for anyone."

- [ ] `pip install -r …` (if MCP uses Python)
- [ ] `claude plugin validate .`
- [ ] `claude --plugin-dir ./my-plugin`
- [ ] `/your-skill` runs
- [ ] Agent invokes MCP tools
- [ ] Hook blocks a known-bad Bash command
- [ ] README install works without your laptop's secrets

---

## 8. Common mistakes

| Mistake | Fix |
|---------|-----|
| MCP with write tools | Remove them — safety is the schema, not the prompt |
| Safety only in a prompt | Hooks enforce; prompts suggest |
| MCP tool names in the skill | Capabilities in skill; names in README + agent |

---

You have the persona framework, a worked example, and a validation checklist. Build the smallest version of your plugin that proves the value to one team, then iterate from real usage rather than imagined requirements.

---

[Official plugin docs](https://code.claude.com/docs/en/plugins) · [Agents](https://code.claude.com/docs/en/agents) · [Hooks guide](https://code.claude.com/docs/en/hooks-guide) · [MCP setup](https://code.claude.com/docs/en/mcp) · [Skills](https://code.claude.com/docs/en/skills)
