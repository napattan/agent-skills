---
name: publish-qgis
description: >
  Deterministic QGIS plugin release preparation, semantic version management, single-root archive packaging, and publication protocol for plugins.qgis.org (/publish-qgis).
  Use this skill when the user asks to publish or update a QGIS plugin, build release zip for QGIS, release to QGIS plugin portal, bump QGIS plugin version, or mentions /publish-qgis.
  Do NOT use for general QGIS canvas GIS modeling (use /qgis instead) or Rhino/Grasshopper plugins (use /publish-food4rhino).
---

# QGIS Plugin Release & Publishing Protocol (`/publish-qgis`)

**Deterministic release packaging and publication protocol for the official QGIS Python Plugins Repository ([plugins.qgis.org](https://plugins.qgis.org)).**  
Eliminates packaging rejections, enforces semantic versioning, and validates metadata against Django/Python `configparser` interpolation constraints.

---

## 1. Non-Negotiable QGIS Packaging Invariants

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE 3 INVARIANTS                                      │
├──────────────────────────┬──────────────────────────┬─────────────────────────────────┤
│ 1. SINGLE-ROOT DIRECTORY │ 2. ZERO RAW `%` IN INI   │ 3. CLASSFACTORY HOOK            │
│ The ZIP file MUST have a │ Python's configparser    │ `__init__.py` MUST define:      │
│ single top-level folder: │ treats `%` as variable   │ ```python                       │
│ `plugin_name/metadata...`│ interpolation.           │ def classFactory(iface):        │
│ NEVER zip files at root! │ Use `percent` or `%%`    │     return MyPlugin(iface)      │
│                          │ in `metadata.txt`.       │ ```                             │
└──────────────────────────┴──────────────────────────┴─────────────────────────────────┘
```

---

## 2. Release Lifecycle: 4 Progressive Steps

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     STEP 1      │     │     STEP 2      │     │     STEP 3      │     │     STEP 4      │
│ Pre-Flight Audit│ ──> │ Version Bump &  │ ──> │ Deterministic   │ ──> │ Portal Upload & │
│ (/publish-audit)│     │ Metadata Lock   │     │ ZIP Packaging   │     │ Git Release Tag │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Step 1: Execute Pre-Flight Security Audit
Before packaging, run `/publish-audit` with the QGIS platform profile:
```bash
python .agents/skills/publish-audit/scripts/audit_engine.py <plugin_dir> --platform qgis
```
* **Verify**: Zero detected API keys, zero hardcoded developer machine paths (`C:\Users\<user>\...`, `/Users/<user>/...`), zero unhandled `B110: try_except_pass` blocks, and zero unescaped `%` symbols in `metadata.txt`.

---

### Step 2: Semantic Version Management & Metadata Verification
QGIS enforces strict unique version numbers per plugin name in its database. You **cannot overwrite** an existing version number via the upload form.

- **Patch release** (`1.1.0` → `1.1.1`): Bug fixes, metadata updates, packaging hotfixes.
- **Minor release** (`1.1.0` → `1.2.0`): New features, additional framing modes, new projection sliders.
- **Major release** (`1.0.0` → `2.0.0`): Breaking architecture changes or QGIS 4 compatibility.

#### Required Fields in `metadata.txt`:
```ini
[general]
name=My Plugin Name
qgisMinimumVersion=3.16
description=Short one-sentence summary in English.
about=Detailed description. If using percentages, write '50 percent' or '50%%' — NEVER raw '%'.
category=Cartography
version=1.1.1
author=Your Name
email=your.personal@email.com
homepage=https://github.com/username/plugin-repo
tracker=https://github.com/username/plugin-repo/issues
repository=https://github.com/username/plugin-repo
experimental=False
deprecated=False
icon=icon.png
tags=axonometric,isometric,cartography,diagram
```

---

### Step 3: Package Release ZIP Archive
Run the deterministic packaging engine:

```bash
# Package current version
python .agents/skills/publish-qgis/scripts/package_qgis.py <plugin_dir>

# OR automatically bump patch version and package:
python .agents/skills/publish-qgis/scripts/package_qgis.py <plugin_dir> --bump patch
```

#### What this script guarantees:
1. Validates all required metadata fields.
2. Checks INI syntax and escapes invalid characters.
3. Packages all source files into a single root directory inside `dist/<plugin_slug>_v<version>.zip`.
4. Automatically strips build debris (`__pycache__`, `.git`, `.DS_Store`, `test_*.py`).
5. Performs immediate un-zip verification to confirm zero orphan files exist at root.

---

### Step 4: Upload to QGIS Official Portal

1. Open your browser and navigate to:
   - **First Release**: [plugins.qgis.org/plugins/add/](https://plugins.qgis.org/plugins/add/)
   - **Update Existing Plugin**: Navigate to `https://plugins.qgis.org/plugins/<id>/` and click **`+ Add version`**.
2. Select the generated archive:
   `<plugin_dir>/dist/<plugin_slug>_v<version>.zip`
3. Confirm the 6 checklist boxes:
   - [✓] ZIP follows single-folder structure (`plugin_name/metadata.txt`).
   - [✓] Repository matches ZIP code.
   - [✓] English description.
   - [✓] Valid public metadata links.
   - [✓] Tested in QGIS.
   - [✓] Email agreement confirmed.
4. Click **Upload**.
5. Tag the release in Git:
   ```bash
   git add metadata.txt
   git commit -m "chore(release): bump version to v<version>"
   git tag -a v<version> -m "Release v<version>"
   git push origin main --tags
   ```

---

## 3. Troubleshooting & Recovery Matrix

| Error Message on Portal | Root Cause | Instant Fix |
| :--- | :--- | :--- |
| `Errors parsing metadata.txt. '%' must be followed by '%' or '('` | Raw unescaped `%` in `description` or `about` | Replace `%` with `percent` or `%%` in `metadata.txt`. |
| `Zip file must contain a single top-level directory` | Zipped loose files without parent folder | Use `package_qgis.py` which automatically prefixes all archive paths with `<plugin_slug>/`. |
| `A plugin with this name and version number already exists` | Attempting to upload duplicate version | Run `package_qgis.py <plugin_dir> --bump patch` to increment version. |
| `Email confirmation pending` | First upload under email address | Click confirmation link sent to the author email address defined in `metadata.txt`. |
