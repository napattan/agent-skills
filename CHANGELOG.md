# Changelog

## v1.0.0

First tagged public line of this skill suite. Skills are host-agnostic: Claude Code, Grok, Gemini/Antigravity, Cursor, Codex, and similar SKILL.md loaders; IDE or CLI; Windows, macOS, and Linux.

### Changed
- `/update-doc` starts from **this chat**, then scans markdown and HTML in the **current workspace**. No baked-in project file list. A project may add its own `scripts/audit_docs.py`. The old thesis HTML auditor is **not** in this package.
- `/create-skill` discovers common skill roots (`.agents`, `.grok`, `~/.claude`, `~/.grok`, `~/.gemini/config`) and writes a full SKILL.md after the description is approved. Not a thin stub. Not Gemini-only.
- `/boostx` feature-detects host tools. It does not require Antigravity-only APIs. Task classes: code, docs, audit.
- `/publish-audit` scans `.env`, `.ps1`, `.sh`, `.toml`. GitHub without LICENSE is blocking. Food4Rhino without `.gha`/`.dll` is blocking. README words like Published / LIVE / 1-click are advisory. Platforms are generic, qgis, food4rhino, github only (no PyPI/NPM claim).

### Install
Clone `skills/` into your host skill root. See README. Tag: `v1.0.0`.
