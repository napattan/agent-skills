---
name: publish-audit
description: >
  Comprehensive pre-flight security, secret, privacy, quality, and packaging audit before publishing packages or plugins to GitHub, QGIS, Food4Rhino, PyPI, or NPM (/publish-audit).
  Use this skill when the user asks to audit before publishing, scan for secrets or tokens, check API keys, run security scan, check privacy/PII, or mentions /publish-audit, "preflight audit", or "check before publish".
  Do NOT use for general code refactoring without publishing intent, UI styling, or live server penetration testing.
---

# Universal Package & Release Pre-Flight Audit (`/publish-audit`)

**High-discipline pre-flight gatekeeper for software releases.**  
Audits codebases, plugins, and packages across **5 core compliance pillars** to guarantee zero credential leaks, zero security vulnerabilities, zero machine path hardcoding, and strict platform compliance before code is made public.

---

## 1. The 5 Compliance Pillars

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE 5 AUDIT PILLARS                                   │
├──────────────────────────┬──────────────────────────┬─────────────────────────────────┤
│ 1. SECRETS & CREDENTIALS │ 2. STATIC SECURITY (AST) │ 3. PRIVACY & PORTABILITY        │
│ • API Keys (OpenAI, AWS, │ • Shell & SQL injection  │ • No machine paths (C:\Users,   │
│   GitHub, Google, Slack) │ • eval(), exec(), compile│   /Users/, /home/)              │
│ • Private SSH/RSA keys   │ • Bandit B110 try-except │ • No local IP addresses / LAN   │
│ • DB connection strings  │ • Insecure temp files    │ • PII & institutional emails    │
├──────────────────────────┼──────────────────────────┼─────────────────────────────────┤
│ 4. CODE QUALITY & SYNTAX │ 5. PACKAGING HYGIENE & PLATFORM COMPLIANCE                 │
│ • Syntax compilation     │ • QGIS: metadata.txt `%` interpolation, single-root zip    │
│ • Undefined variables    │ • Food4Rhino: Compiled .gha/.dll assembly, sample .gh      │
│ • Unused imports / bloat │ • GitHub: README.md, OSI LICENSE, .gitignore               │
│ • Type annotation checks │ • Debris elimination (__pycache__, .DS_Store, build logs)  │
└──────────────────────────┴──────────────────────────┴─────────────────────────────────┘
```

---

## 2. Platform Compliance Profiles

Run the audit with the target platform profile to activate tailored checks:

| Platform Profile | Specific Rules Checked | Common Blocking Failure Mode |
| :--- | :--- | :--- |
| **`--platform qgis`** | • `metadata.txt` required fields (`name`, `version`, `author`, `email`, `about`).<br>• Literal `%` character escaping (`%%` or `percent`) to prevent Python `configparser` interpolation crashes.<br>• Single-root directory structure inside release `.zip` (`<plugin_dir>/...`).<br>• Zero `.pyc`, `.git`, or scratch files in archive. | `InterpolationSyntaxError: '%' must be followed by '%' or '('` |
| **`--platform food4rhino`** | • Compiled C# `.gha` or `.dll` assembly present.<br>• Ready-to-run `.gh` sample / benchmark canvas present.<br>• Compatibility flags (Rhino 7 / Rhino 8 .NET Core).<br>• Rhino Package Manager (`yak spec` / `manifest.yml`). | Uploading raw uncompiled `.cs` without `.gha` assembly |
| **`--platform github`** | • OSI-compliant `LICENSE` file present.<br>• Polished `README.md` with installation and badges.<br>• Production `.gitignore` preventing build artifacts from tracking.<br>• Zero sensitive environment variables (`.env`, `.secrets`). | Leaking `.env` or tracking `__pycache__` |
| **`--platform generic`** | • Universal secret scanning, AST analysis, machine user paths, and debris check. | Hardcoded developer directory paths |

---

## 3. Step-by-Step Audit Protocol

When `/publish-audit` is triggered, execute the following workflow:

### Step 1: Run the Standalone Audit Engine
Execute the bundled cross-platform audit engine:

```bash
# General syntax:
python scripts/audit_engine.py <target_directory> --platform <generic|qgis|food4rhino|github>

# Example: QGIS plugin audit
python scripts/audit_engine.py ./qgis-axonometric-transformer --platform qgis

# Example: Food4Rhino plugin package audit
python scripts/audit_engine.py ./SAE-Core --platform food4rhino
```

### Step 2: Run External Static Linters (If Installed)
Supplement the engine with system-level security and quality scanners:

```bash
# 1. Bandit Static Security (Python)
bandit -r <target_dir> -x "**/test_*.py,**/scratch/**"

# 2. Flake8 Quality & Critical Syntax Check
flake8 <target_dir> --exclude="test_*.py" --max-line-length=120 --select=E9,F63,F7,F82,F401,F841

# 3. Detect Secrets Scan
detect-secrets scan <target_dir>
```

### Step 3: Evaluate Findings Matrix

Categorize all identified findings into two tiers:
1. **BLOCKING ERRORS (Must fix before release)**:
   - Any detected API key, token, private key, or database password.
   - Any hardcoded developer machine path (`C:\Users\...`, `/Users/...`).
   - Unescaped `%` in QGIS `metadata.txt`.
   - Python `SyntaxError` or `F821` (undefined variable).
   - Insecure `shell=True` or `eval()` / `exec()` calls without explicit design justification.
   - QGIS release `.zip` missing the single-root folder structure.
2. **ADVISORIES (Recommended optimizations)**:
   - Unused imports (`F401`) or unused local variables (`F841`).
   - Missing sample `.gh` canvas for Grasshopper tools.
   - Broad `except Exception: pass` without `# nosec B110` or logging.

### Step 4: Apply Ponytail Surgical Fixes
- Fix root causes with the shortest working diff.
- Never add external dependencies to solve a linter warning.
- Re-run the audit engine until **Blocking Errors: 0**.

---

## 4. Verification & Output Clearance Certificate

When the audit completes, output the official clearance certificate in the conversation:

```text
======================================================================
🛡️ PRE-FLIGHT AUDIT CLEARANCE CERTIFICATE
======================================================================
Target Package:    <package_name>
Target Platform:   <QGIS / Food4Rhino / GitHub>
Files Scanned:     <N> files

[✓] Secrets & Tokens:      PASS (0 credentials or high-entropy tokens)
[✓] Security & AST:        PASS (0 command injections / dynamic calls)
[✓] Privacy & Paths:       PASS (0 machine-specific paths hardcoded)
[✓] Code Quality:          PASS (0 syntax errors / 0 undefined symbols)
[✓] Packaging Hygiene:     PASS (0 build artifacts / single-root verified)
----------------------------------------------------------------------
VERDICT: ✨ GREEN (Approved for Public Release)
======================================================================
```

---

## 5. Security & Invariant Rules
- **No Masked Secrets Logged**: If a potential secret is flagged, the output report must mask it (`sk-1234...cdef`) to prevent leaking the secret into conversation logs.
- **Cross-Platform UTF-8**: Always run with UTF-8 stdout streams to prevent `cp1252` encoding crashes on Windows.
- **Zero Temporary Debris**: Any scratch test files created during verification must be deleted before concluding the turn.
