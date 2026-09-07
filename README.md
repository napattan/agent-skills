# ⚡ Agent Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-v1.0.0-blue.svg)](https://github.com/napattan/agent-skills/releases/tag/v1.0.0)
[![Platforms](https://img.shields.io/badge/Platforms-Claude_•_Grok_•_Gemini_•_Cursor_•_Codex-8A2BE2)](#-universal-installation)
[![Dual-OS](https://img.shields.io/badge/Dual--OS-Windows_•_macOS_•_Linux-success)](#-the-boostx-engineering-discipline)
[![Verification](https://img.shields.io/badge/Protocol-BoostX_Verified-emerald)](#-the-boostx-engineering-discipline)

> Portable developer protocols for AI coding assistants (Claude Code, Grok, Gemini/Antigravity, Cursor, Codex, and similar), IDE or CLI, Windows, macOS, and Linux.

---

## 🚀 Universal 1-Line Installation

Install into your preferred AI agent environment with one command:

Clone this repo, then copy or link the `skills/` folder into **your host's skill root**. Same SKILL.md files; the host only cares where they sit.

| Host | Typical skill root |
|:---|:---|
| Claude Code | `~/.claude/skills` or `<repo>/.claude/skills` |
| Grok | `$GROK_HOME/skills` or `~/.grok/skills` or `<repo>/.grok/skills` |
| Gemini / Antigravity | `~/.gemini/config/skills` |
| Cursor / Codex / other IDEs | often `<repo>/.agents/skills` |

```bash
# Claude Code (POSIX)
git clone https://github.com/napattan/agent-skills.git ~/.claude/skills

# Grok (POSIX)
git clone https://github.com/napattan/agent-skills.git ~/.grok/skills

# Gemini / Antigravity (POSIX)
git clone https://github.com/napattan/agent-skills.git ~/.gemini/config/skills

# Project (many IDEs)
git clone https://github.com/napattan/agent-skills.git .agents/skills
```

Windows PowerShell examples use `$env:USERPROFILE\.claude\skills`, `$env:USERPROFILE\.grok\skills`, `$env:USERPROFILE\.gemini\config\skills`.

Or run `scripts/install.ps1` / `scripts/install.sh` (copies into roots that already exist on this machine).

---

## 📦 The Core Suite

| Skill | Command | Description | What It Solves |
| :--- | :---: | :--- | :--- |
| **BoostX Protocol** | `/boostx` | **High-discipline root-cause engineering protocol**. Enforces a mandatory 4-phase lifecycle: (1) Red Invariant Gate, (2) Ponytail Anti-Bloat Ladder, (3) Dual-OS Surgical Standards, and (4) Ruthless 3-Tier Verification. | Stops AI agents from writing speculative code, guessing at bug symptoms, or introducing bloated abstractions. |
| **Skill Creator** | `/create-skill` | Scaffold a portable SKILL.md for the current host (Claude, Grok, Gemini, Codex, Cursor). Full skill after description approval; dual-OS; no machine-user paths. | Stops thin stubs, wrong install folders, and host-only drafts. |
| **Release Pre-Flight** | `/publish-audit` | **Automated security, secret, privacy & packaging audit**. Scans codebases for leaked API keys, tokens, private keys, Bandit vulnerabilities, Flake8 errors, hardcoded machine paths, and platform rules (QGIS, Food4Rhino, GitHub). | Prevents credential leaks, server interpolation errors, security flags, and broken release packages before going public. |
| **QGIS Publisher** | `/publish-qgis` | **Deterministic QGIS plugin release packager & manager**. Validates `metadata.txt` against INI interpolation bugs, enforces single-root folder zip structure, manages SemVer bumps, runs AST-level Qt6 / QGIS 4 forward-compatibility checks ('QGIS 4 Ready' badge), and resolves package slugs via a 5-rung continuity ladder. | Eliminates plugin portal upload rejections, `%` interpolation crashes, folder name mismatches, and Qt6 deprecation blocks. |
| **Doc Synchronizer** | `/update-doc` | Sync docs from **this chat** plus markdown/HTML in the **current workspace**. No baked-in project file list. | Stops stale claims after a change, on any repo. |

---

## 🛡️ The BoostX Engineering Discipline

Every skill in this repository is built to eliminate the common failure modes of AI tools (context bloat, undertriggering, hardcoded environment paths, and broken links):

```
┌────────────────────────────────────────────────────────┐
│  1. THE RED INVARIANT GATE                             │
│     • Explicit failure modes defined before creation   │
│     • Positive trigger keywords + negative exclusions  │
│     • Context budget: YAML description ≤ 1024 chars    │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  2. PONYTAIL ANTI-BLOAT LADDER                         │
│     • Prefer Markdown instructions over custom scripts │
│     • Reuse existing CLI tools & shell utilities       │
│     • Shortest working instructions win                │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  3. DUAL-OS PORTABILITY INVARIANTS                     │
│     • Zero machine-specific absolute paths (`C:\...`)  │
│     • Universal POSIX forward slashes (`/`) in links   │
│     • UTF-8 stream reconfigured for Windows terminals  │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  4. RUTHLESS 3-TIER VERIFICATION                       │
│     • Tier 1: Static YAML frontmatter & regex linting  │
│     • Tier 2: Link target existence & secret audit     │
│     • Tier 3: Physical directory & slash menu proof    │
└────────────────────────────────────────────────────────┘
```

---

## 🔗 Related Toolkits

Looking for automated MCP bridges for CAD, Parametric Modeling, GIS, and Vector Graphics? Check out our sister repository:
* 🏛️ **[mcp-bridges](https://github.com/napattan/mcp-bridges)**: Production-grade MCP bridges for **Rhino, Grasshopper, QGIS, Adobe Illustrator, and Figma**.

---

## 👤 Author

**Napat Phasundhiae**  
*Computational Design Technologist | Spatial Analytics • Urban & Environmental Simulation • Workflow Automation*

* **GitHub**: [@napattan](https://github.com/napattan)
* **LinkedIn**: [Napat Phasundhiae](https://www.linkedin.com/in/napatphas/)

---

## 📄 License

This repository is open-source under the [MIT License](LICENSE).
