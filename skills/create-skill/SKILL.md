---
name: create-skill
description: >
  Author portable agent skills (SKILL.md plus optional scripts/references) for any SKILL.md host.
  Use when the user says create skill, make this a skill, turn this workflow into a skill, /create-skill,
  or wants to scaffold, distill, lint, or globalize an agent skill.
  Do NOT use for editing application source, publishing packages, or general documentation sync
  (use /publish-audit, /publish-qgis, /update-doc instead).
---

# Create Skill (portable)

Build a skill that works on Claude Code, Grok, Gemini/Antigravity, Codex, Cursor, and similar loaders, in IDE or CLI, on Windows, macOS, and Linux.

Do not hardcode one vendor path, one machine, or one workspace. After the user accepts the description, write a **full** SKILL.md (not a stub).

---

## 1. Scope: pick a skill root

Ask **project vs user**, then detect which roots exist. If several exist, list them and let the user pick.

**Project (share with the repo):**

| Host family | Directory |
|:---|:---|
| Antigravity / many IDEs | `<workspace>/.agents/skills/<name>/` |
| Grok | `<workspace>/.grok/skills/<name>/` |
| Claude Code (project) | `<workspace>/.claude/skills/<name>/` |

Default project root: `.agents/skills/<name>/` if that tree exists, else `.grok/skills/<name>/`, else create `.agents/skills/<name>/`.

**User (all workspaces on this machine):**

| Host family | Directory |
|:---|:---|
| Claude Code | `~/.claude/skills/<name>/` |
| Grok | `$GROK_HOME/skills/<name>/` if set, else `~/.grok/skills/<name>/` |
| Gemini / Antigravity | `~/.gemini/config/skills/<name>/` |

Never write a personal cloud path (OneDrive, iCloud) into SKILL.md. Resolve `~` at install time only.

Create a **real directory**, not a nested junction or `skill/skill` copy.

Windows: `New-Item -ItemType Directory -Force`. POSIX: `mkdir -p`. Or Python `pathlib.Path.mkdir(parents=True)`.

---

## 2. Interview (short)

1. **Name:** `^[a-z0-9]+(-[a-z0-9]+)*$`, 2-64 chars.
2. **What it should do** and **when not to**.
3. **Red failure:** what the agent gets wrong without this skill.

Optional Mode A: distill this chat (successful steps only). Do not require a vendor transcript file.

If the need is a two-line preference, put it in the project's agent rules file instead of a skill.

---

## 3. Description draft (must approve)

Show the YAML `description` (what it does, slash command, triggers, `Do NOT use for`). Wait for approve or edit. Then write files.

---

## 4. Write a full SKILL.md

```
<name>/
├── SKILL.md
├── references/     optional
└── scripts/        optional, Python stdlib only
```

Frontmatter:

```yaml
---
name: <name>
description: >
  <one sentence>.
  Use when <triggers, /name>.
  Do NOT use for <exclusions>.
---
```

Body rules:

- Actionable steps, not an essay. Prefer existing CLIs over new scripts.
- POSIX `/` in links. No `C:\Users\<user>` or `/Users/<user>/` in published text.
- Dual-shell or Python for commands.
- User-facing/release copy the skill will generate: no em/en dashes (ASCII hyphen is fine). No LaTeX. ASCII diagrams allowed **inside SKILL.md only**.
- Python scripts start with UTF-8 stdout reconfigure.

---

## 5. Verify before declaring done

1. `name` regex and `description` <= 1024 chars, with a `Do NOT use` clause.
2. Relative links resolve. No backslashes in markdown link targets.
3. No secrets; no machine user paths (allow `<user>` placeholders).
4. No `skill/skill` nested folder.
5. `python -m py_compile` on any `scripts/*.py`.
6. Tell the user **which host slash menu** will see it (the root you wrote to).

Report: name, scope, path, `/name`, verification pass.
