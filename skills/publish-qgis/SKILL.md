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
│ 1. SINGLE-ROOT DIRECTORY │ 2. ZERO RAW `%` IN INI   │ 3. CLASSFACTORY HOOK     │ 4. QT6 / QGIS 4 SCOPING│
│ The ZIP file MUST have a │ Python's configparser    │ `__init__.py` MUST       │ All enums must be     │
│ single top-level folder: │ treats `%` as variable   │ define:                  │ scoped and imported via│
│ `plugin_name/metadata...`│ interpolation.           │ ```python                │ `qgis.PyQt` shim to   │
│ NEVER zip files at root! │ Use `percent` or `%%`    │ def classFactory(iface): │ earn the green        │
│                          │ in `metadata.txt`.       │     return MyPlugin(iface│ "QGIS 4 Ready" badge. │
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

### Step 1: Execute Pre-Flight Security & Qt6 Audits
Before packaging, run both the security audit and the Qt6 forward-compatibility scan:

```bash
# 1. Run Pre-Flight Security & Privacy Scan
python .agents/skills/publish-audit/scripts/audit_engine.py <plugin_dir> --platform qgis

# 2. Run Qt6 / QGIS 4 Forward-Compatibility AST Linter
python .agents/skills/publish-qgis/scripts/check_qt6.py <plugin_dir>
```

* **Security Gate**: Zero detected API keys, zero hardcoded developer machine paths (`C:\Users\<user>\...`), zero unhandled `B110: try_except_pass` blocks, and zero unescaped `%` symbols in `metadata.txt`.
* **Qt6 Gate**: Zero unscoped enums, zero direct `PyQt5` imports, and zero deprecated Qt6 methods.

---

### Step 2: Semantic Version Management & Metadata Verification
QGIS enforces strict unique version numbers per plugin name in its database. You **cannot overwrite** an existing version number via the upload form.

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
version=1.1.2
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
# Package current version (automatically runs Qt6 validation gate)
python .agents/skills/publish-qgis/scripts/package_qgis.py <plugin_dir>

# OR automatically bump patch version and package:
python .agents/skills/publish-qgis/scripts/package_qgis.py <plugin_dir> --bump patch

# (Optional) Bypass Qt6 check if packaging legacy QGIS 2/3-only branch:
python .agents/skills/publish-qgis/scripts/package_qgis.py <plugin_dir> --skip-qt6
```

#### What this script guarantees:
1. **Mandatory Qt6 Gate**: Validates all Python files against the AST compliance visitor before creating archive.
2. **Metadata Validation**: Validates all required fields, INI syntax, and escapes invalid characters.
3. **Single-Root Architecture**: Packages all source files into a single root directory inside `dist/<plugin_slug>_v<version>.zip`.
4. **Build Debris Elimination**: Automatically strips `__pycache__`, `.git`, `.DS_Store`, `test_*.py`, and scratch files.
5. **Post-Build Unzip Verification**: Performs immediate unzip verification to confirm zero orphan files exist at the zip root.

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

## 4. Troubleshooting & Recovery Matrix

| Error Message on Portal | Root Cause | Instant Fix |
| :--- | :--- | :--- |
| `Qt6 Check [N issues]` (Red Tab) | Unscoped Qt enums (e.g. `Qt.AlignCenter`) or direct `PyQt5` import | Run `python .agents/skills/publish-qgis/scripts/check_qt6.py <plugin_dir>` to list exact lines and replacements. Re-package and upload. |
| `Errors parsing metadata.txt. '%' must be followed by '%' or '('` | Raw unescaped `%` in `description` or `about` | Replace `%` with `percent` or `%%` in `metadata.txt`. |
| `Zip file must contain a single top-level directory` | Zipped loose files without parent folder | Use `package_qgis.py` which automatically prefixes all archive paths with `<plugin_slug>/`. |
| `A plugin with this name and version number already exists` | Attempting to upload duplicate version | Run `package_qgis.py <plugin_dir> --bump patch` to increment version. |
| `Email confirmation pending` | First upload under email address | Click confirmation link sent to the author email address defined in `metadata.txt`. |
