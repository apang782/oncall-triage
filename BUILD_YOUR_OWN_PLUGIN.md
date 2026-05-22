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

## 4. Decision tree: MCP vs hook vs skill-only

```text
Need live data from a system?     → MCP (read-only tools first)
Need to block dangerous commands? → PreToolUse hook (exit 2 = deny)
Just need consistent procedure?   → Skill only
Long investigation eating context?→ Agent
```

**Enterprise safety:** Prefer *read-only by construction* (MCP tool list has no writes) over prompt pleading ("please don't delete").

---

## 5. Case study: observability triage (this repo)

**Pain:** Browser-driven log/metrics search is slow and untokenizable; agents silently "succeed" with wrong env prefixes or dropped CLI flags.

**Patterns we baked in:**

| Pattern | Where |
|---------|--------|
| MCP before browser | `agents/triage.md` |
| Silent-failure checks | `skills/incident-triage/SKILL.md` |
| Mock MCP for workshops | `mcp-servers/mock-observability/` |
| Defence in depth | skill (procedure) + hook (Bash deny list) |

**Fork for your org:**

1. Copy `skills/incident-triage/SKILL.md` → rename, edit steps 2–3 for your runbooks (PagerDuty link, escalation policy).
2. Copy `agents/triage.md` → point at *your* MCP tool names.
3. Replace `.mcp.json` mock entry with your OpenSearch/Grafana MCP configs (keep tools read-only).
4. Extend `scripts/pre_tool_guard.py` with your banned commands (`aws s3 rm`, `helm uninstall`, etc.).

---

## 6. Testing checklist (fresh clone)

- [ ] `pip install -r …` (if MCP uses Python)
- [ ] `claude plugin validate .`
- [ ] `claude plugin install ./my-plugin`
- [ ] `/your-skill` runs
- [ ] Agent invokes MCP tools
- [ ] Hook blocks a known-bad Bash command
- [ ] README works without your laptop's secrets

---

## 7. Common mistakes

| Mistake | Fix |
|---------|-----|
| Stub agent ("you are helpful…") | Give ordered workflow + tool priority |
| MCP with write tools | Delete tools; safety is the schema |
| Hook only in prompt | Users bypass prompts; hooks don't |
| 10 skills | One skill, one agent, iterate |
| README is marketing fluff | Copy-paste install + 3-step demo |

---

## 8. Where to go next

- [Create plugins](https://code.claude.com/docs/en/plugins) — official authoring flow
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference) — hooks events, `${CLAUDE_PLUGIN_ROOT}`
- [Skills](https://code.claude.com/docs/en/skills) — `SKILL.md` frontmatter

When your plugin works for one team, publish an internal marketplace entry and run a 90-minute "build your first plugin" lab using sections 1–6 above.
