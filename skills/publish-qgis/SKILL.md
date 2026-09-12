---
name: publish-qgis
description: >
  Deterministic QGIS plugin release preparation, semantic version management, single-root archive packaging, Qt6/QGIS 4 forward-compatibility verification ('QGIS 4 Ready' badge), and publication protocol for plugins.qgis.org (/publish-qgis).
  Use this skill when the user asks to publish or update a QGIS plugin, build release zip for QGIS, release to QGIS plugin portal, bump QGIS plugin version, verify Qt6 compatibility, or mentions /publish-qgis.
  Do NOT use for general QGIS canvas GIS modeling (use /qgis instead) or Rhino/Grasshopper plugins (use /publish-food4rhino).
---

# QGIS Plugin Release & Publishing Protocol (`/publish-qgis`)

**Deterministic release packaging, Qt6 forward-compatibility enforcement, and publication protocol for the official QGIS Python Plugins Repository ([plugins.qgis.org](https://plugins.qgis.org)).**  
Eliminates packaging rejections, enforces semantic versioning, guarantees the green **"QGIS 4 Ready"** badge, and validates metadata against Django/Python `configparser` interpolation constraints.

---

## 1. Non-Negotiable QGIS Packaging Invariants

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           THE 4 INVARIANTS                                             │
├──────────────────────────┬──────────────────────────┬──────────────────────────┬───────────────────────┤
│ 1. ROOT SLUG CONTINUITY  │ 2. ZERO RAW `%` IN INI   │ 3. CLASSFACTORY HOOK     │ 4. QT6 / QGIS 4 SCOPING│
│ The ZIP file MUST have a │ Python's configparser    │ `__init__.py` MUST       │ All enums must be     │
│ single top folder that   │ treats `%` as variable   │ define:                  │ scoped and imported via│
│ matches the portal's     │ interpolation.           │ ```python                │ `qgis.PyQt` shim to   │
│ original package_name!   │ Use `percent` or `%%`    │ def classFactory(iface): │ earn the green        │
│ NEVER zip files at root! │ in `metadata.txt`.       │     return MyPlugin(iface│ "QGIS 4 Ready" badge. │
│                          │                          │ ```                      │                       │
└──────────────────────────┴──────────────────────────┴──────────────────────────┴───────────────────────┘
```

---

## 2. Qt6 / QGIS 4 Forward-Compatibility Protocol ("QGIS 4 Ready")

When plugins are uploaded to `plugins.qgis.org`, the portal executes an automated AST migration check (`pyqt5_to_pyqt6.py`). Any unscoped enum or direct `PyQt5` import triggers red warning banners and blocks the **"QGIS 4 Ready"** badge.

### Scoped Enum Migration Reference

| Legacy / Unscoped PyQt5 | Scoped Qt6 / QGIS 4 (Portable via `qgis.PyQt`) |
| :--- | :--- |
| `Qt.AlignCenter` | `Qt.AlignmentFlag.AlignCenter` |
| `Qt.KeepAspectRatio` | `Qt.AspectRatioMode.KeepAspectRatio` |
| `Qt.IgnoreAspectRatio` | `Qt.AspectRatioMode.IgnoreAspectRatio` |
| `Qt.SmoothTransformation` | `Qt.TransformationMode.SmoothTransformation` |
| `Qt.Horizontal` / `Qt.Vertical` | `Qt.Orientation.Horizontal` / `Qt.Orientation.Vertical` |
| `QFrame.NoFrame` | `QFrame.Shape.NoFrame` |
| `Qt.ScrollBarAlwaysOff` | `Qt.ScrollBarPolicy.ScrollBarAlwaysOff` |
| `QSizePolicy.Expanding` / `Fixed` | `QSizePolicy.Policy.Expanding` / `QSizePolicy.Policy.Fixed` |
| `QComboBox.AdjustTo...WithIcon` | `QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon` |
| `QKeySequence.Copy` | `QKeySequence.StandardKey.Copy` |
| `QImage.Format_ARGB32_Premultiplied` | `QImage.Format.Format_ARGB32_Premultiplied` |
| `QImage.Format_ARGB32` | `QImage.Format.Format_ARGB32` |
| `QPainter.Antialiasing` | `QPainter.RenderHint.Antialiasing` |
| `QPainter.SmoothPixmapTransform` | `QPainter.RenderHint.SmoothPixmapTransform` |
| `QPainter.HighQualityAntialiasing` | **Removed in Qt6.** Use `QPainter.RenderHint.Antialiasing`. |
| `Qt.RoundCap` | `Qt.PenCapStyle.RoundCap` |
| `Qt.RoundJoin` | `Qt.PenJoinStyle.RoundJoin` |
| `Qt.SolidLine` | `Qt.PenStyle.SolidLine` |
| `Qt.NoBrush` | `Qt.BrushStyle.NoBrush` |
| `Qt.transparent` | `Qt.GlobalColor.transparent` |
| `Qt.IntersectClip` | `Qt.ClipOperation.IntersectClip` |
| `Qt.OddEvenFill` | `Qt.FillRule.OddEvenFill` |
| `QIODevice.ReadOnly` / `WriteOnly` | `QIODevice.OpenModeFlag.ReadOnly` / `WriteOnly` |
| `Qt.WaitCursor` | `Qt.CursorShape.WaitCursor` |
| `QgsWkbTypes.PolygonGeometry` | `QgsWkbTypes.GeometryType.PolygonGeometry` |
| `QgsUnitTypes.LayoutMillimeters` | `QgsUnitTypes.LayoutUnit.LayoutMillimeters` |
| `QPageSize.Point` / `Millimeter` | `QPageSize.Unit.Point` / `QPageSize.Unit.Millimeter` |
| `QPageLayout.Portrait` / `Landscape` | `QPageLayout.Orientation.Portrait` / `QPageLayout.Orientation.Landscape` |

> [!IMPORTANT]
> **Zero Direct `from PyQt5` Imports:** Never import directly from `PyQt5.QtCore` or `PyQt5.QtGui`, even in fallback `except ImportError` blocks. Always import from `qgis.PyQt.*`.

---

## 3. Release Lifecycle: 4 Progressive Steps

```
┌─────────────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│         STEP 1          │     │     STEP 2      │     │     STEP 3      │     │     STEP 4      │
│ Pre-Flight Security &   │ ──> │ Version Bump &  │ ──> │ Deterministic   │ ──> │ Portal Upload & │
│ Qt6 Compatibility Audit │     │ Metadata Lock   │     │ ZIP Packaging   │     │ Git Release Tag │
└─────────────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Step 1: Execute Pre-Flight Audits
Before packaging, run the universal security, Flake8, and Qt6 forward-compatibility scan:

```bash
# 1. Run Pre-Flight Security, Privacy & Flake8 Scan
python .agents/skills/publish-audit/scripts/audit_engine.py <plugin_dir> --platform qgis

# 2. Run Qt6 / QGIS 4 Forward-Compatibility AST Linter directly
python .agents/skills/publish-qgis/scripts/check_qt6.py <plugin_dir>
```

* **Security & Secrets Gate**: Zero detected API keys (AWS, GitHub, HF, PyPI, OpenAI), zero hardcoded developer machine paths (`C:\Users\<user>\...`), zero unhandled `B110: try_except_pass` blocks, and zero unescaped `%` symbols in `metadata.txt`.
* **Flake8 Quality Gate**: Zero style or lint violations against the local `.flake8` configuration.
* **Qt6 Gate**: Zero unscoped enums, zero direct `PyQt5` imports, and zero deprecated Qt6 methods.

---

### Step 2: Semantic Version Management & Metadata Verification
QGIS enforces strict unique version numbers per plugin name in its database. You **cannot overwrite** an existing version number via the upload form.

**Uploaded occupies the number even if not approved.** The public listing may say "no public version yet" while `1.1.0` / `1.1.2` already exist in the database. Do not reuse an unused *lower* number (for example `1.1.1`) while a higher one is already uploaded: Plugin Manager picks the highest version string, so the older zip would win if both were later approved. Always `--bump patch` from the **highest uploaded** version, not from the last public one.

- **Patch release** (`1.1.0` → `1.1.1`): Bug fixes, metadata updates, packaging hotfixes, Qt6 forward scoping.
- **Minor release** (`1.1.0` → `1.2.0`): New features, additional framing modes, new projection sliders.
- **Major release** (`1.0.0` → `2.0.0`): Breaking architecture changes or native QGIS 4 architecture.

#### Required Fields in `metadata.txt`:
```ini
[general]
name=My Plugin Name
qgisMinimumVersion=3.16
description=Short one-sentence summary in English.
about=Detailed description. If using percentages, write '50 percent' or '50%%' — NEVER raw '%'.
category=Cartography
version=1.0.0
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

### Step 3: Package Release ZIP Archive (5 Integrated Quality Gates)
Run the deterministic packaging engine:

```bash
# Package current version (automatically enforces all 5 gates):
python .agents/skills/publish-qgis/scripts/package_qgis.py <plugin_dir>

# Automatically bump patch version and package:
python .agents/skills/publish-qgis/scripts/package_qgis.py <plugin_dir> --bump patch

# Explicitly override internal package folder name:
python .agents/skills/publish-qgis/scripts/package_qgis.py <plugin_dir> --package-name <slug>

# (Optional overrides for debugging):
# --skip-qt6        Bypass Qt6 check
# --skip-flake8     Bypass Flake8 check
# --skip-security   Bypass secret/path check
```

#### Deterministic Package Name Resolution Ladder:
To guarantee that the root folder inside the ZIP always matches the portal's registered `package_name` (avoiding `Plugin folder name mismatch` rejections), `package_qgis.py` evaluates this 5-rung ladder:
1. **CLI Flag (`--package-name <slug>`)**: Highest priority manual override.
2. **Metadata Key (`package_name=<slug>` in `metadata.txt`)**: **Recommended Best Practice.** Setting `package_name` in `metadata.txt` locks the canonical package name into git as the SSOT.
3. **Previous Release Archive Inspection (`dist/*.zip`)**: Automatically inspects existing release archives in `dist/` and adopts the prior root prefix to guarantee 100% version-to-version continuity.
4. **Git Wrapper Affix Stripping**: Automatically detects and strips common git wrapper prefixes (`qgis-*`, `qgis_*`) or suffixes (`*-qgis`, `*-plugin`).
5. **Folder Name**: Sanitized lowercase directory name fallback.

#### What this script guarantees:
1. **Root Slug Continuity**: Enforces exact root folder name matching across all version releases.
2. **Mandatory Qt6 Gate**: Validates all Python files against the AST compliance visitor before creating archive.
3. **Mandatory Flake8 Gate**: Runs Flake8 against `.flake8` config and halts if style/syntax errors exist.
4. **Mandatory Security Gate**: Scans for leaked tokens/credentials and developer machine user paths (`C:\Users\<user>`).
5. **Metadata Validation**: Validates all required fields, INI syntax, and escapes invalid characters.
6. **Deterministic ZIP Timestamps & Permissions**: Normalizes file timestamps to a fixed epoch and standard `0o644` permissions for reproducible builds without leaking author machine states.
7. **Build Debris Elimination**: Automatically strips `__pycache__`, `.git`, `.DS_Store`, `test_*.py`, scratch files, and portal scanner configs (`.flake8`, `.bandit`, `.secrets.baseline`). Shipping those configs marks the version **Validated (configured)** and asks admins to review suppressed rules. Keep them in git for local lint; never put them in the ZIP. Portal flake8 already uses `--max-line-length=120`.
8. **Post-Build Unzip Verification**: Performs immediate unzip verification to confirm zero orphan files exist at the zip root. Confirm the namelist has no `.flake8` / `.bandit` / `.secrets.baseline`.

---

### Step 4: Upload to QGIS Official Portal

1. Open your browser and navigate to:
   - **First Release**: [plugins.qgis.org/plugins/add/](https://plugins.qgis.org/plugins/add/)
   - **Update Existing Plugin**: Navigate to `https://plugins.qgis.org/plugins/<id>/` and click **`+ Add version`**.
2. Select the generated archive:
   `<plugin_dir>/dist/<plugin_slug>_v<version>.zip`
3. Optional **Changelog** box: one short English patch note (not mandatory).
4. Confirm the 6 checklist boxes:
   - [✓] ZIP follows single-folder structure (`plugin_name/metadata.txt`).
   - [✓] Repository matches ZIP code.
   - [✓] English description.
   - [✓] Valid public metadata links.
   - [✓] Tested in QGIS.
   - [✓] Email agreement confirmed.
5. Click **Upload**. Wait for the Security Scan tab. Required outcome: 0 critical, and **no** "Developer-Supplied Config Files" / **Validated (configured)** banner. Target status is plain **Validated**. If the banner appears, the ZIP shipped a scanner config; bump patch and re-upload.
6. Tag the release in Git:
   ```bash
   git add metadata.txt
   git commit -m "chore(release): bump version to v<version>"
   git tag -a v<version> -m "Release v<version>"
   git push origin main --tags
   ```

---

## 4. Troubleshooting & Recovery Matrix

| Error Message on Portal | Root Cause | Instant Fix |
| :--- | :--- | :--- |
| `Plugin folder name mismatch: ... (X) is different from the original (Y)` | The original version was registered with root folder `Y`, but current package uses `X`. | Add `package_name=Y` to `metadata.txt` (or run `package_qgis.py <dir> --package-name Y`). Re-package and upload. |
| `Qt6 Check [N issues]` (Red Tab) | Unscoped Qt enums (e.g. `Qt.AlignCenter`) or direct `PyQt5` import | Run `python .agents/skills/publish-qgis/scripts/check_qt6.py <plugin_dir>` to list exact lines and replacements. Re-package and upload. |
| `Errors parsing metadata.txt. '%' must be followed by '%' or '('` | Raw unescaped `%` in `description` or `about` | Replace `%` with `percent` or `%%` in `metadata.txt`. |
| `Zip file must contain a single top-level directory` | Zipped loose files without parent folder | Use `package_qgis.py` which automatically prefixes all archive paths with `<plugin_slug>/`. |
| `A plugin with this name and version number already exists` | Attempting to upload a version string that is already in the database, including **unapproved** uploads | Run `package_qgis.py <plugin_dir> --bump patch` from the highest uploaded version. Do not roll back to an unused lower number. |
| `Email confirmation pending` | First upload under email address | Click confirmation link sent to the author email address defined in `metadata.txt`. |
| `Validated (configured)` / Developer-Supplied Config Files | ZIP contains `.flake8`, `.bandit`, or `.secrets.baseline`. Portal uses those files during the scan and asks admins to review suppressed rules. | Leave those files in git for local lint. Do not ship them. `package_qgis.py` strips them. Re-package with `--bump patch` (you cannot overwrite an existing version). |
