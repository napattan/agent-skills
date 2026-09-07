# Agent Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-v1.0.0-blue.svg)](https://github.com/napattan/agent-skills/releases/tag/v1.0.0)
[![Platforms](https://img.shields.io/badge/Platforms-Claude_•_Grok_•_Gemini_•_Cursor_•_Codex-8A2BE2)](#-universal-installation)
[![Dual-OS](https://img.shields.io/badge/Dual--OS-Windows_•_macOS_•_Linux-success)](#-portable-by-design)
[![Verification](https://img.shields.io/badge/Protocol-BoostX_Verified-emerald)](#-portable-by-design)

> **Portable developer protocols for AI coding assistants.**  
> Same SKILL.md files on Claude Code, Grok, Gemini/Antigravity, Cursor, Codex, and similar loaders. IDE or CLI. Windows, macOS, and Linux. Not locked to one machine or one repo.

Sister repo: **[mcp-bridges](https://github.com/napattan/mcp-bridges)** (QGIS, Rhino, Grasshopper, Illustrator, Figma).

---

## Universal installation

Clone this repository, then put the `skills/` folder into **your host's skill root**. The files do not change per host.

| Host | Typical skill root |
|:---|:---|
| Claude Code | `~/.claude/skills` or `<repo>/.claude/skills` |
| Grok | `$GROK_HOME/skills` or `~/.grok/skills` or `<repo>/.grok/skills` |
| Gemini / Antigravity | `~/.gemini/config/skills` |
| Cursor / Codex / other IDEs | often `<repo>/.agents/skills` |

```bash
git clone https://github.com/napattan/agent-skills.git ~/.claude/skills
git clone https://github.com/napattan/agent-skills.git ~/.grok/skills
git clone https://github.com/napattan/agent-skills.git ~/.gemini/config/skills
git clone https://github.com/napattan/agent-skills.git .agents/skills
```

Windows PowerShell: `$env:USERPROFILE\.claude\skills`, `$env:USERPROFILE\.grok\skills`, `$env:USERPROFILE\.gemini\config\skills`.

Or run `scripts/install.ps1` (Windows) / `scripts/install.sh` (macOS, Linux). The installer copies into roots that already exist on this machine (`--claude`, `--grok`, `--antigravity`, or a workspace path).

Pin a known line with the tag: `git clone --branch v1.0.0 https://github.com/napattan/agent-skills.git`

---

## The suite

```
agent-skills/skills/
├── /boostx           high-discipline bugs and code changes
├── /create-skill     author a portable SKILL.md for the current host
├── /update-doc       sync markdown/HTML from this chat + this workspace
├── /publish-audit    pre-flight secrets, paths, GitHub / QGIS / Food4Rhino
└── /publish-qgis     QGIS plugin zip, SemVer, Qt6 / QGIS 4 checks
```

| Skill | Command | What it does | What it stops |
|:---|:---|:---|:---|
| **BoostX** | `/boostx` | Red gate, Ponytail short-diff ladder, dual-OS edits, green verification. Task classes: **code** (failing command), **docs** (stale-claim grep), **audit** (engine exit code). Uses host subagents/background tools **if they exist**; never requires a vendor API name. | Speculative patches, fake unit tests on doc work, Antigravity-only instructions on Grok/Claude/Codex |
| **Create Skill** | `/create-skill` | Picks a skill root (project `.agents` / `.grok` or user `~/.claude` / `~/.grok` / `~/.gemini/config`). Drafts YAML `description`, waits for approval, writes a **full** SKILL.md (not a stub). Dual-OS mkdir. No machine-user paths. | Thin drafts, wrong folder, Gemini-only or Grok-only write paths |
| **Update Doc** | `/update-doc` | (1) Ground-truth delta from **this chat**. (2) Scan markdown and HTML in the **current workspace**. (3) Follow relations (symbols, metrics, status words, links). (4) 5-tier inner-to-outer sync. (5) Re-grep deprecated terms to zero. Optional: run **your** `scripts/audit_docs.py` if you added one. | Stale claims, hardcoded file lists from someone else's repo, "update everything on disk" |
| **Publish Audit** | `/publish-audit` | `python scripts/audit_engine.py <dir> --platform generic\|qgis\|food4rhino\|github`. Secrets (masked), machine paths, `.env` / `.ps1` / `.sh` / `.toml`. GitHub missing LICENSE = blocking. Food4Rhino missing `.gha`/`.dll` = blocking. README "Published" / "LIVE" / "1-click" = advisory. | Credential leaks, unescaped `%` in QGIS `metadata.txt`, claiming PyPI/NPM without a profile |
| **Publish QGIS** | `/publish-qgis` | SemVer, `metadata.txt` interpolation, single-root zip, Qt6 / QGIS 4 AST check, package slug ladder. Run **after** `/publish-audit` is green. | Plugin portal zip rejections, Qt6 deprecations, folder-name mismatches |

Public status words (owned by `/update-doc`): **LIVE**, **REGISTERED**, **PREPARED**, **IN PIPELINE**, **DRAFT**. Do not write LIVE or 1-click install without a receipt.

---

## Portable by design

- **Any host:** feature-detect tools. Never require `invoke_subagent`, `DeepCoder`, `manage_task`, or other vendor-only names.
- **Any OS:** POSIX `/` in files; PowerShell and POSIX examples, or Python stdlib. No `C:\Users\<you>` in published text.
- **Any repo:** `/update-doc` does not ship a thesis auditor or a baked-in filename list. Your project may add `scripts/audit_docs.py`.
- **Typography for user-facing/release copy:** no em/en dashes (ASCII hyphen is fine). No LaTeX.

BoostX ladder (used by all skills here): YAGNI, reuse, stdlib, shortest diff. YAML `description` stays short, with a `Do NOT use for` clause.

---

## Repository layout

```
agent-skills/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── skills/
│   ├── boostx/SKILL.md
│   ├── create-skill/SKILL.md
│   ├── update-doc/SKILL.md
│   ├── publish-audit/
│   │   ├── SKILL.md
│   │   └── scripts/audit_engine.py
│   └── publish-qgis/
│       ├── SKILL.md
│       └── scripts/check_qt6.py, package_qgis.py
└── scripts/
    ├── install.sh
    └── install.ps1
```

---

## Related toolkits

- **[mcp-bridges](https://github.com/napattan/mcp-bridges):** MCP bridges for **QGIS, Rhino 3D, Grasshopper, Adobe Illustrator, and Figma**.

---

## Author

**Napat Phasundhiae**  
*Computational Design Technologist | Spatial Analytics • Urban & Environmental Simulation • Workflow Automation*

- GitHub: [@napattan](https://github.com/napattan)
- LinkedIn: [linkedin.com/in/napatphas](https://www.linkedin.com/in/napatphas/)

## License

[MIT License](LICENSE)
