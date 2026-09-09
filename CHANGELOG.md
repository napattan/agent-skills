# Changelog

## v1.2.0

- `/update-doc`: major upgrade to the cross-document synchronization protocol:
  - **Interactive HTML & Web Artifact Parity**: explicitly governs slide decks, architecture viewers, and dashboard portals. Mandates DOM container parity (`<section class="slide">`), sequential heading counters (`SLIDE 01 / N`), embedded JavaScript state (`totalSlides = N`), and repository CSS design token compliance.
  - **Distribution Mirrors & Shadow References Invariant**: detects duplicated documents across distribution or export bundles (`dist/docs/`, `package/docs_reference/`) and enforces deterministic byte-for-byte synchronization.
  - **Historical Boundary Protocol**: separates active SSOT invariants (must hit zero stale references) from immutable historical changelogs / ADRs (preserving past event context).
  - **Cross-Platform Scripting Hygiene**: mandates Python standard library scratch execution with UTF-8 stdout reconfiguration for multi-line DOM / regex replacements, eliminating shell-specific CLI quote mangling.
- `/update-doc`: added dedicated MIT LICENSE file and clean scripts guidance for standalone packaging.

### Install

See README. Tag: `v1.2.0`.
```bash
git clone --branch v1.2.0 https://github.com/napattan/agent-skills.git
```

## v1.1.0

- `/brief`: load related workspace markdown (cap 8), then do `/brief <task>` in the same turn. HTML only when the task is a specific page. Portable: no baked-in filename list.
- `/create-skill`: machine-path ban uses `C:\Users\<user>` so `/publish-audit --platform github` does not treat ellipsis placeholders as a real home path.

### Install

See README. Tag: `v1.1.0`.
```bash
git clone --branch v1.1.0 https://github.com/napattan/agent-skills.git
```

## v1.0.0

First tagged public line of this skill suite.

**Who it is for:** anyone who wants the same `/boostx`, `/create-skill`, `/update-doc`, `/publish-audit`, and `/publish-qgis` behavior on Claude Code, Grok, Gemini/Antigravity, Cursor, or Codex, in an IDE or a CLI, on Windows, macOS, or Linux.

**Who it is not for:** a drop-in thesis-workspace auditor. That HTML checker is not in this package. Add `scripts/audit_docs.py` in **your** repo if you need extra checks.

### Skills in this release

| Command | Role in v1.0.0 |
|:---|:---|
| `/boostx` | Red / Ponytail / dual-OS / green. Task classes: code, docs, audit. Host tools are optional. |
| `/create-skill` | Discover skill roots, approve description, write a full SKILL.md. |
| `/update-doc` | Chat delta + workspace markdown/HTML scan + relation sync + zero-stale grep. |
| `/publish-audit` | Pre-flight engine for generic, qgis, food4rhino, github. |
| `/publish-qgis` | QGIS zip / SemVer / Qt6 packager (unchanged role; still the zip SSOT). |

### Changed (vs untagged `main` before this tag)

- `/update-doc` no longer assumes one author's filenames or a bundled thesis HTML auditor.
- `/create-skill` is not Gemini-only and does not stop at a stub README.
- `/boostx` does not require Antigravity `invoke_subagent` / `DeepCoder` / `manage_task`.
- `/publish-audit` scans `.env` and shell/toml; GitHub LICENSE and Food4Rhino `.gha` are blocking; README overclaim is advisory; no PyPI/NPM platform claim.

### Install

See README. Tag: `v1.0.0`.
```bash
git clone --branch v1.0.0 https://github.com/napattan/agent-skills.git
```
