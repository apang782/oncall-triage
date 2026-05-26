# Build your own Claude Code plugin (customer guide)

**Audience:** A platform engineer at a large org who wants a plugin for *their* workflow—not Anthropic internal docs.

**Time to first win:** ~30 minutes for skill + agent; add MCP or hooks when you need external data or guardrails.

---

## 1. Start with persona + pain (not `plugin.json`)

Write one sentence:

> *Who* is stuck, *what* are they doing, *what breaks today*?

Example: *"On-call SREs lose 20 minutes opening Dashboards tabs when paging fires."*

Your plugin should solve **one** job. Everything else is scope creep.

---

## 2. Minimum viable plugin

| Piece | When you need it |
|-------|------------------|
| **Skill** (`skills/<name>/SKILL.md`) | Repeatable checklist the user or Claude invokes (`/your-skill`) |
| **Agent** (`agents/<name>.md`) | Multi-step work that burns context—delegate to a subagent |
| **MCP** (`.mcp.json`) | External systems: logs, metrics, tickets, CMDB |
| **Hook** (`hooks/hooks.json`) | Hard guardrails: block deletes, warn on `apply`, audit egress |

**Rule:** Ship **skill + agent + (MCP or hook)**. Don't add components to check boxes.

### Portable skill vs concrete agent (important)

| Artifact | Should contain | Should not contain |
|----------|------------------|-------------------|
| **Skill** | Procedure: inputs, step order, guards (zero pods, unknown args, facts before hypotheses) | Your vendor’s exact MCP tool names (`cluster_overview`, `search_logs`, …) |
| **Agent** | Tool priority + **this plugin’s** server/tool names for your demo or product | A second copy of the whole playbook (keep in skill) |
| **README** | **Tool mapping** table: capability → your server → tool names | — |
| **`.mcp.json`** | Server launch config | Business logic |

**Why:** If the skill names demo-only tools, every customer must fork the skill when they plug in OpenSearch or Grafana. If the skill names *capabilities* (“read-only metrics overview”, “log search”), customers only change MCP config + agent prompt.

**Fork checklist for observability triage:**

1. Copy the skill → adjust runbook steps (escalation, ticketing)—**not** MCP tool strings unless you lack an agent.
2. Copy the agent → wire **your** `mcp__…` tool names and server id.
3. Replace `.mcp.json` → read-only tools only on the MCP surface.
4. Document your mapping in **your** README (copy the table from oncall-triage).

### Standard layout

```text
my-plugin/
├── .claude-plugin/plugin.json   # metadata (name required)
├── skills/my-workflow/SKILL.md
├── agents/specialist.md
├── hooks/hooks.json             # optional
├── .mcp.json                    # optional
└── README.md                    # install in <5 min
```

---

## 3. Build order (30 / 60 / 90 minutes)

1. **Skill first** — bullet steps, inputs, stop conditions. Easiest to test: `/my-skill`.
2. **Agent second** — paste skill workflow into agent prompt; add tool priority ("MCP before Bash").
3. **MCP or hook last** — only when the skill can't be honest without them.

Validate early: `claude plugin validate ./my-plugin`

---

## 4. Spec-first when design is non-trivial

For a 3-hour plugin, a short spec is enough. For production MCPs or multi-team rollouts, spec-first avoids shipping the wrong abstraction.

**Write before code (one page):**

- Persona + pain (one paragraph)
- Components: skill / agent / MCP / hook — and what each will *not* do
- Tool surface (names, read-only vs write, example JSON shape)
- Open questions (auth, silent-failure footguns, demo vs prod backends)

**Implement after** alignment. Land **producers** (read-only MCP, skill checklist) before **consumers** (automated summarizers, ticket writers, playbook generators)—gate consumers until cost, loop, and trust controls exist.

This repo followed that split: mock MCP + skill + hook in scope; automated post-triage playbooks explicitly out of scope.

---

## 5. Decision tree: MCP vs hook vs skill-only

```text
Need live data from a system?     → MCP (read-only tools first)
Need to block dangerous commands? → PreToolUse hook (exit 2 = deny)
Just need consistent procedure?   → Skill only
Long investigation eating context?→ Agent
```

**Enterprise safety:** Prefer *read-only by construction* (MCP tool list has no writes) over prompt pleading ("please don't delete").

---

## 6. Case study: observability triage (this repo)

**Pain:** Browser-driven log/metrics search is slow and untokenizable; agents silently "succeed" with wrong env prefixes or dropped CLI flags.

**Patterns we baked in:**

| Pattern | Where |
|---------|--------|
| MCP before browser | `agents/triage.md` |
| Portable skill (capabilities, not tool names) | `skills/incident-triage/SKILL.md` |
| Concrete tool mapping | README **Design** section + `agents/triage.md` |
| `unknown_args_warning` (no silent defaults) | mock `search_logs` (production servers should emulate) |
| Mock MCP for workshops | `mcp-servers/mock-observability/` |
| Defence in depth | skill (procedure) + hook (Bash deny list) |

**Fork for your org:**

1. Copy `skills/incident-triage/SKILL.md` → edit runbook/escalation steps; **keep capability-based** unless you have no agent.
2. Copy `agents/triage.md` → set *your* MCP server id and tool names.
3. Add a README tool-mapping table (capability → server → tool).
4. Replace `.mcp.json` with your read-only OpenSearch/Grafana MCP configs.
5. Extend `scripts/pre_tool_guard.py` with your banned commands (`aws s3 rm`, `helm uninstall`, etc.).

---

## 7. Testing checklist (fresh clone)

- [ ] `pip install -r …` (if MCP uses Python)
- [ ] `claude plugin validate .`
- [ ] `claude --plugin-dir ./my-plugin`
- [ ] `/your-skill` runs
- [ ] Agent invokes MCP tools
- [ ] Hook blocks a known-bad Bash command
- [ ] README works without your laptop's secrets

---

## 8. Common mistakes

| Mistake | Fix |
|---------|-----|
| Stub agent ("you are helpful…") | Give ordered workflow + tool priority |
| MCP with write tools | Delete tools; safety is the schema |
| Hook only in prompt | Users bypass prompts; hooks don't |
| 10 skills | One skill, one agent, iterate |
| README is marketing fluff | Copy-paste install + 3-step demo |
| MCP tool names in the skill | Capabilities in skill; names in README + agent |

---

## 9. Where to go next

- [Create plugins](https://code.claude.com/docs/en/plugins) — official authoring flow
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference) — hooks events, `${CLAUDE_PLUGIN_ROOT}`
- [Skills](https://code.claude.com/docs/en/skills) — `SKILL.md` frontmatter

When your plugin works for one team, publish an internal marketplace entry and run a 90-minute "build your first plugin" lab using sections 1–6 above.
