---
name: brief
description: >
  Load related workspace markdown, then do the user's task in the same turn.
  Use when the user runs /brief, /brief <task>, or says read the docs then,
  get ready and, or brief then.
  Do NOT use for documentation sync (/update-doc), publishing (/publish-audit,
  /publish-qgis), creating skills (/create-skill), or session recap (/handoff).
argument-hint: "<task>"
disable-model-invocation: true
---

# `/brief` (portable)

Read a small set of related **markdown** in the **current workspace**, then do the user's task. Same SKILL.md on Claude Code, Grok, Gemini/Antigravity, Cursor, Codex, and similar loaders. IDE or CLI. Windows, macOS, Linux. Not locked to one machine or one repo.

Do not invent a filename list. Do not crawl the whole tree. Do not paste file bodies back to the user.

Red failure: answering from memory and contradicting the workspace source of truth, or starting work before the plan/handoff that already locked the next step.

## When not to

| Need | Use instead |
|:---|:---|
| Sync or rewrite docs | `/update-doc` |
| Pre-flight or QGIS zip | `/publish-audit`, `/publish-qgis` |
| Author a skill | `/create-skill` |
| Write a session recap | `/handoff` |

If the task is only one of those, name that skill and stop.

## SOP (every run)

### 1. Parse the task

Slash arguments, or the rest of the user message after `/brief`. Files the user attached or named are seeds, not the corpus.

No task: discover, show the briefing table, **stop**. Do not invent work.

### 2. Seed terms

From the task: identifiers, product names, status words, paths. Drop stopwords.

### 3. Discover markdown

Search `*.md` in the current workspace, including hidden skill/config dirs when the host allows.

Exclude: `.git`, `node_modules`, `dist`, `__pycache__`, `.venv`, vendor bundles.

Use whatever search exists:

- Host `grep` / `rg --hidden` if present
- PowerShell `Select-String`
- Do not require `rg`

Existence check (do not require these names): `AGENTS.md`, `CONTEXT.md`, root `README.md`, `START_HERE.md`, `HANDOFF.md`, names matching `*STRATEGY*`, `*PLAN*`, `CAREER_*`. These are **types**, not a baked-in project.

Grep seed terms in `*.md`.

Rank, then cap at **8** files:

1. User-attached or named paths
2. Short named sources of truth (strategy, plan, handoff, start-here, career, root README)
3. Hit count

Prefer one source of truth over five copies of the same claim. If `AGENTS.md` is already in context, do not re-read it; note it as already loaded.

Files longer than about 200 lines: headings plus matching sections, not the whole file.

### 4. HTML gate

Skip HTML by default.

Open HTML only if the task is about a page the user will see (html, css, dashboard, layout, "this page") **and** a specific path is named or sits in the relation set. Then that file only. Never crawl all HTML. Do not ingest source or data dumps as briefing material; the later task step may open code as usual.

### 5. Briefing table

| File | Why | Locked fact I will obey |

If two docs disagree, list the conflict before editing public claims.

Public-status words (LIVE, REGISTERED, PREPARED, IN PIPELINE, DRAFT) are owned by `/update-doc`. Obey that vocabulary. Do not invent a second glossary.

User-facing/release copy: no em/en dashes (hyphen `-` is fine). No LaTeX.

### 6. Do the task

Execute the parsed task, obeying the locked facts. Do not start `/update-doc` or rewrite strategy docs unless the task asked for that.

## Rubric

- [ ] Task parsed, or empty-args stop after the table
- [ ] Markdown discovered with the host's search; cap 8
- [ ] HTML skipped unless the page-gate fired
- [ ] Briefing table shown; conflicts listed
- [ ] Task done, or deferred to the skill in **When not to**
