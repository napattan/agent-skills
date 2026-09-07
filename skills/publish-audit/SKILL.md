---
name: publish-audit
description: >
  Pre-flight security, secret, privacy, quality, and packaging audit before publishing
  to GitHub, QGIS, or Food4Rhino (/publish-audit).
  Use when the user asks to audit before publish, scan for secrets or tokens, check API keys,
  or run /publish-audit, preflight audit, or check before publish.
  Do NOT use for general refactoring, UI styling, live penetration testing, or doc-only sync
  (use /update-doc). Do NOT use for QGIS zip/Qt6 packaging mechanics (use /publish-qgis).
---

# `/publish-audit` (portable)

Pre-flight for a **target directory** the user names. Works on any OS. No workspace-specific paths.

---

## Platforms (honest list)

Engine flag `--platform`: `generic` | `qgis` | `food4rhino` | `github` only. Do not claim PyPI or NPM until those profiles exist.

| Profile | Blocking (must fix) | Advisory |
|:---|:---|:---|
| **qgis** | Missing/empty `metadata.txt` required fields; unescaped `%`; Python syntax; secrets; machine user paths | Debris; zip shape (prefer `/publish-qgis` for the release zip) |
| **food4rhino** | Secrets; machine paths; **no `.gha`/`.dll`** | Missing sample `.gh` |
| **github** | Secrets; machine paths; **no LICENSE** | Missing README; debris; README words Published / LIVE / 1-click install without a receipt |
| **generic** | Secrets; machine paths; syntax | Debris; README/LICENSE |

Public-claim **vocabulary** (LIVE, REGISTERED, PREPARED, IN PIPELINE) is owned by `/update-doc`. This skill only **advises** on Published / LIVE / 1-click in README files.

User-facing lines you print: no em/en dashes (hyphen `-` is fine).

---

## Protocol

### 1. Run the engine

From this skill's folder (or any copy of `scripts/audit_engine.py`):

```text
python scripts/audit_engine.py <target_directory> --platform <generic|qgis|food4rhino|github>
```

Use a path relative to the user's project, not a hardcoded machine home.

### 2. Optional extra linters (if the user's machine has them)

```text
bandit -r <target_dir> -x "**/test_*.py,**/scratch/**"
flake8 <target_dir> --exclude="test_*.py" --max-line-length=120 --select=E9,F63,F7,F82,F401,F841
```

If they are missing, skip. The engine result still stands.

### 3. Blocking vs advisory

**Blocking:** credentials; machine user paths (`C:\Users\<name>`, `/Users/<name>`, `/home/<name>`); unescaped `%` in QGIS metadata; `SyntaxError` / undefined names; unjustified `eval`/`exec`/`shell=True`; GitHub with no LICENSE; Food4Rhino with no compiled assembly.

**Advisory:** unused imports; debris; README overclaim words; missing sample `.gh`; broad `except: pass`.

### 4. Fix with a short diff. Re-run until blocking = 0.

---

## Output

Match the engine stdout. When blocking is 0:

```text
PRE-FLIGHT AUDIT
Target:    <dir>
Platform:  <platform>
Files:     <n>
Blocking:  0
Advisory:  <n>
VERDICT: PASS (safe to publish for this platform)
```

If a secret is found, mask it (`abcd...wxyz`). UTF-8 stdout. Delete scratch files you created.

Do not reimplement `/publish-qgis` zip/Qt6/slug logic here. For a QGIS **release zip**, run `/publish-qgis` after this audit is green.
