---
name: publish-audit
description: >
  Pre-flight security, secret, privacy, quality, Flake8 compliance, and packaging audit before publishing
  to GitHub, QGIS, or Food4Rhino (/publish-audit).
  Use when the user asks to audit before publish, scan for secrets or tokens, check API keys,
  or run /publish-audit, preflight audit, or check before publish.
  Do NOT use for general refactoring, UI styling, live penetration testing, or doc-only sync
  (use /update-doc). Do NOT use for QGIS zip/Qt6 packaging mechanics (use /publish-qgis).
---

# `/publish-audit` (portable & 100% risk-proof)

Pre-flight security, privacy, and code quality engine for a **target directory**. Works on any OS. No workspace-specific paths.

---

## Platforms & Security Gates

Engine flag `--platform`: `generic` | `qgis` | `food4rhino` | `github`.

| Profile | Blocking (must fix before release) | Advisory |
|:---|:---|:---|
| **qgis** | Credentials / tokens (HF, PyPI, AWS, OpenAI, GitHub, Slack); machine user paths (`C:\Users\<user>`); unescaped `%` in `metadata.txt`; missing required metadata fields; `__init__.py` lacking `classFactory(iface)`; Qt6/QGIS 4 AST violations; Flake8 lint/syntax errors; unsafe `eval`/`exec`/`shell=True`/`pickle` | Packaging debris; missing icon; broad `except: pass` |
| **food4rhino** | Secrets; machine paths; **no `.gha`/`.dll`**; unsafe code | Missing sample `.gh` |
| **github** | Secrets; machine paths; **no LICENSE**; Flake8 violations | Missing README; debris; README words Published / LIVE / 1-click install without receipt |
| **generic** | Secrets; machine paths; syntax errors; Flake8 violations | Debris; README/LICENSE |

Public-claim **vocabulary** (LIVE, REGISTERED, PREPARED, IN PIPELINE) is owned by `/update-doc`. This skill only **advises** on Published / LIVE / 1-click in README files.

---

## 5-Pillar Security & Quality Architecture

1. **Secrets & Privacy Gate (Zero Leaks)**:
   - Scans against high-entropy patterns: AWS, GitHub Classic & Fine-Grained, OpenAI, Anthropic, Google AI, HuggingFace, PyPI, GitLab, NPM, RSA/SSH keys, DB connection strings.
   - Dual-OS Invariant: strictly blocks machine user paths (`C:\Users\<user>`, `/Users/<user>`, `/home/<user>`).
2. **AST Vulnerability Inspector**:
   - Blocks dynamic execution: `eval()`, `exec()`, `compile()`.
   - Blocks shell injection: `os.system()`, `subprocess.*(..., shell=True)`.
   - Blocks unsafe deserialization: `pickle.load()`, `pickle.loads()`.
   - Blocks unsafe temp files: `tempfile.mktemp()`.
3. **Flake8 Code Quality Gate**:
   - Automatically executes Flake8 audit against the project's local `.flake8` configuration.
   - Blocks releases on syntax errors, undefined variables, and style violations.
4. **Platform Invariant Enforcer**:
   - QGIS: Validates `metadata.txt` (zero unescaped `%`), verifies `def classFactory(iface)` in `__init__.py`, and checks Qt6/QGIS 4 readiness via `check_qt6.py`.
   - Food4Rhino: Verifies compiled `.gha`/`.dll` assembly.
   - GitHub: Verifies OSI-compliant `LICENSE`.
5. **Packaging Hygiene**:
   - Detects build debris (`.pyc`, `Thumbs.db`, `.DS_Store`, `.swp`, `.env`).

---

## Protocol

### 1. Run the engine

From this skill's folder (or any copy of `scripts/audit_engine.py`):

```bash
python .agents/skills/publish-audit/scripts/audit_engine.py <target_directory> --platform <generic|qgis|food4rhino|github>
```

### 2. Flags

- `--skip-flake8`: Bypass Flake8 code quality checks (if flake8 is temporarily unavailable).
- `--skip-qt6`: Bypass Qt6 AST forward-compatibility check for QGIS platform.

### 3. Output Format

```text
======================================================================
PRE-FLIGHT AUDIT SCORECARD
======================================================================
Target:    <target_dir>
Platform:  <platform>
Files:     <count>
Blocking:  0
Advisory:  <count>
----------------------------------------------------------------------
✅ VERDICT: PASS (100% Risk-Proof & Safe to Publish)
```

If a secret is found, the engine automatically masks it (`abcd...wxyz`).
For generating the deterministic QGIS release zip after audit passes, run `/publish-qgis`.
