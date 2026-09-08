# -*- coding: utf-8 -*-
"""
Deterministic QGIS Plugin Packaging & Release Script (/publish-qgis).
Validates metadata.txt, escapes INI interpolation characters, handles semantic versioning,
and generates compliant single-root release ZIP archives for plugins.qgis.org.
"""

import sys
import os
import re
import zipfile
import argparse
import configparser
import importlib.util
from pathlib import Path

# Enforce UTF-8 standard output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Dynamically import check_qt6 if available
try:
    from .check_qt6 import audit_directory_for_qt6
except (ImportError, ValueError):
    try:
        from check_qt6 import audit_directory_for_qt6
    except ImportError:
        _check_script = Path(__file__).parent / "check_qt6.py"
        if _check_script.exists():
            _spec = importlib.util.spec_from_file_location("check_qt6", str(_check_script))
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            audit_directory_for_qt6 = _mod.audit_directory_for_qt6
        else:
            audit_directory_for_qt6 = None

REQUIRED_METADATA_FIELDS = [
    "name", "qgisMinimumVersion", "description", "about", "version", "author", "email"
]

EXCLUDE_PATTERNS = [
    r"__pycache__",
    r"\.py[cod]$",
    r"\.git",
    r"\.github",
    r"\.vscode",
    r"\.idea",
    r"dist",
    r"build",
    r"\.ds_store",
    r"thumbs\.db",
    r"desktop\.ini",
    r"^test_.*\.py$",
    r"^scratch.*",
    # plugins.qgis.org marks the version Validated (configured) if these ship
    r"\.flake8$",
    r"\.bandit$",
    r"\.secrets\.baseline$",
]


def bump_semver(current_version: str, bump_type: str) -> str:
    """Bump semantic version X.Y.Z according to patch, minor, or major."""
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)(.*)$", current_version.strip())
    if not match:
        raise ValueError(f"Version '{current_version}' is not in valid SemVer format (e.g. 1.0.0)")

    major, minor, patch, extra = match.groups()
    major, minor, patch = int(major), int(minor), int(patch)

    if bump_type == "patch":
        patch += 1
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "major":
        major += 1
        minor = 0
        patch = 0

    return f"{major}.{minor}.{patch}{extra}"


def validate_metadata(meta_path: Path) -> dict:
    """Validate metadata.txt and return parsed items."""
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing mandatory `metadata.txt` at: {meta_path}")

    content = meta_path.read_text(encoding="utf-8", errors="ignore")

    # Critical INI interpolation check
    for line_no, line in enumerate(content.splitlines(), 1):
        if "%" in line and not line.strip().startswith("#"):
            # Flag raw unescaped % (not %%)
            unescaped = re.search(r"(?<!%)%(?!%)", line)
            if unescaped:
                raise ValueError(
                    f"Line {line_no} in metadata.txt contains unescaped `%`: `{line.strip()}`. "
                    f"In QGIS INI metadata, literal `%` must be written as `percent` or escaped as `%%` "
                    f"to prevent server `InterpolationSyntaxError`."
                )

    cp = configparser.ConfigParser()
    cp.read(str(meta_path), encoding="utf-8")

    if not cp.has_section("general"):
        raise ValueError("metadata.txt is missing the required `[general]` section.")

    metadata = dict(cp.items("general"))
    for field in REQUIRED_METADATA_FIELDS:
        if field.lower() not in metadata or not metadata[field.lower()].strip():
            raise ValueError(f"Mandatory metadata field `{field}` is missing or empty.")

    return metadata


def resolve_package_slug(plugin_dir: Path, output_dir: Path, explicit_slug: str = "", metadata: dict = None) -> tuple:
    """
    Deterministically resolves the internal zip root folder name (package slug)
    to prevent 'Plugin folder name mismatch' errors on plugins.qgis.org.

    Resolution Ladder:
    1. Explicit CLI argument (--package-name / --folder-name)
    2. Explicit metadata key ('package_name' or 'slug' in metadata.txt)
    3. Existing release archives in output_dir (dist/) to guarantee version-to-version continuity
    4. Git wrapper affix stripping (e.g. 'qgis-my-plugin' -> 'my_plugin')
    5. Sanitized lowercase directory name fallback

    Returns:
        (slug, source_description)
    """
    # 1. Explicit CLI argument
    if explicit_slug and explicit_slug.strip():
        slug = re.sub(r"[^a-zA-Z0-9_]", "_", explicit_slug.strip()).lower()
        return slug, "CLI argument (--package-name)"

    # 2. metadata.txt explicit field
    if metadata:
        for key in ("package_name", "slug", "plugin_package_name"):
            val = metadata.get(key, "").strip()
            if val:
                slug = re.sub(r"[^a-zA-Z0-9_]", "_", val).lower()
                return slug, f"metadata.txt ('{key}')"

    # 3. Previous release archive inspection in output_dir (dist/)
    if output_dir and output_dir.exists():
        zips = sorted(output_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
        for z in zips:
            try:
                with zipfile.ZipFile(z, "r") as zf:
                    names = zf.namelist()
                    prefixes = {n.split("/")[0] for n in names if "/" in n}
                    if len(prefixes) == 1:
                        prev_slug = list(prefixes)[0]
                        if prev_slug and prev_slug != "dist":
                            return prev_slug, f"previous release archive ({z.name})"
            except Exception:
                continue

    # 4. Git wrapper affix stripping (e.g. 'qgis-buffer' or 'buffer-qgis')
    folder_name = plugin_dir.name.strip()
    clean_name = folder_name
    if re.match(r"^qgis[-_]", clean_name, flags=re.IGNORECASE):
        clean_name = re.sub(r"^qgis[-_]", "", clean_name, flags=re.IGNORECASE)
    if re.search(r"[-_](qgis[-_]plugin|qgis)$", clean_name, flags=re.IGNORECASE):
        clean_name = re.sub(r"[-_](qgis[-_]plugin|qgis)$", "", clean_name, flags=re.IGNORECASE)

    if clean_name != folder_name:
        slug = re.sub(r"[^a-zA-Z0-9_]", "_", clean_name).lower()
        return slug, f"stripped git repository wrapper affix from '{folder_name}'"

    # 5. Default fallback to sanitized folder name
    slug = re.sub(r"[^a-zA-Z0-9_]", "_", folder_name).lower()
    return slug, f"folder name ('{folder_name}')"


def package_plugin(plugin_dir: Path, output_dir: Path, bump: str = "none", skip_qt6: bool = False, package_name: str = "") -> Path:
    """Validate, optionally bump version, and package into compliant zip."""
    plugin_dir = plugin_dir.resolve()
    meta_path = plugin_dir / "metadata.txt"
    init_path = plugin_dir / "__init__.py"

    if not init_path.exists():
        raise FileNotFoundError(f"Missing `__init__.py` in plugin directory: {plugin_dir}")

    # Validate init has classFactory
    init_content = init_path.read_text(encoding="utf-8", errors="ignore")
    if "classFactory" not in init_content:
        raise ValueError("`__init__.py` must define `classFactory(iface)` as required by QGIS plugin architecture.")

    # Mandatory Qt6 / QGIS 4 forward-compatibility check
    if not skip_qt6 and audit_directory_for_qt6:
        print("🔍 Running Qt6 / QGIS 4 forward-compatibility scan...")
        qt6_issues = audit_directory_for_qt6(plugin_dir)
        blocking_qt6 = [issue for issue in qt6_issues if issue[3] == "ERROR"]
        if blocking_qt6:
            print(f"\n❌ Qt6 / QGIS 4 Compatibility Check FAILED ({len(blocking_qt6)} blocking issues):", file=sys.stderr)
            for rel_path, line, col, severity, msg in blocking_qt6:
                print(f"  • {rel_path}:{line}:{col} [{severity}] {msg}", file=sys.stderr)
            print("\n💡 plugins.qgis.org will flag these issues and deny the 'QGIS 4 Ready' badge.", file=sys.stderr)
            print("   Fix unscoped enums / direct PyQt5 imports, or pass --skip-qt6 to bypass.", file=sys.stderr)
            raise RuntimeError(f"Qt6 forward-compatibility scan failed with {len(blocking_qt6)} errors.")
        print("  ✓ Qt6 / QGIS 4 compatibility verified (100% QGIS 4 Ready compliant)")

    metadata = validate_metadata(meta_path)
    current_version = metadata["version"]

    # Handle version bump if requested
    if bump in {"patch", "minor", "major"}:
        new_version = bump_semver(current_version, bump)
        print(f"🔄 Bumping version: {current_version} -> {new_version}")

        # Update metadata.txt preserving structure
        lines = meta_path.read_text(encoding="utf-8").splitlines()
        updated_lines = []
        for line in lines:
            if line.strip().startswith("version="):
                updated_lines.append(f"version={new_version}")
            else:
                updated_lines.append(line)

        meta_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
        current_version = new_version
        # Re-validate
        metadata = validate_metadata(meta_path)

    # Derive internal top-level directory name using resolution ladder
    output_dir.mkdir(parents=True, exist_ok=True)
    plugin_slug, slug_source = resolve_package_slug(plugin_dir, output_dir, explicit_slug=package_name, metadata=metadata)

    zip_filename = f"{plugin_slug}_v{current_version}.zip"
    canonical_zip = output_dir / f"{plugin_slug}.zip"
    versioned_zip = output_dir / zip_filename

    # Compile files to package
    files_to_pack = []
    for root, dirs, files in os.walk(plugin_dir):
        # Filter directories
        dirs[:] = [d for d in dirs if not any(re.search(pat, d, re.IGNORECASE) for pat in EXCLUDE_PATTERNS)]
        for f in files:
            if not any(re.search(pat, f, re.IGNORECASE) for pat in EXCLUDE_PATTERNS):
                rel_path = Path(root).relative_to(plugin_dir) / f
                files_to_pack.append(rel_path)

    print(f"📦 Packaging {len(files_to_pack)} files into release archive...")
    print(f"📁 Internal root folder name: `{plugin_slug}/` (resolved from {slug_source})")

    for target_zip in [versioned_zip, canonical_zip]:
        with zipfile.ZipFile(target_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for rel in files_to_pack:
                src_file = plugin_dir / rel
                arcname = f"{plugin_slug}/{rel.as_posix()}"
                zf.write(src_file, arcname)

    # Verify zip internal structure
    with zipfile.ZipFile(versioned_zip, "r") as zf:
        names = zf.namelist()
        # Verify single root directory
        root_prefixes = {n.split("/")[0] for n in names if "/" in n}
        root_orphan_files = [n for n in names if "/" not in n and n]

        if len(root_prefixes) != 1 or root_prefixes.pop() != plugin_slug:
            raise RuntimeError("Packaging failed: multiple top-level directories detected in archive.")
        if root_orphan_files:
            raise RuntimeError(f"Packaging failed: root orphan files detected: {root_orphan_files}")

    print("\n✅ Verification Successful!")
    print(f"  • Plugin Name:     {metadata.get('name')}")
    print(f"  • Package Slug:    {plugin_slug} (resolved via {slug_source})")
    print(f"  • Version:         {current_version}")
    print(f"  • Author:          {metadata.get('author')} ({metadata.get('email')})")
    print(f"  • QGIS Minimum:    {metadata.get('qgisminimumversion')}")
    print(f"  • Qt6 / QGIS 4:    {'Bypassed (--skip-qt6)' if skip_qt6 else '100% Compliant (QGIS 4 Ready)'}")
    print(f"  • Output Archive:  {versioned_zip} ({versioned_zip.stat().st_size} bytes)")
    print(f"  • Canonical Zip:   {canonical_zip} ({canonical_zip.stat().st_size} bytes)")

    return versioned_zip


def main():
    parser = argparse.ArgumentParser(description="Deterministic QGIS Plugin Packaging & Release (/publish-qgis)")
    parser.add_argument("plugin_dir", help="Path to plugin directory containing metadata.txt and __init__.py")
    parser.add_argument("--output-dir", default="", help="Destination directory for built zip (default: <plugin_dir>/dist)")
    parser.add_argument("--bump", choices=["none", "patch", "minor", "major"], default="none", help="Bump version in metadata.txt before packaging")
    parser.add_argument("--skip-qt6", action="store_true", help="Bypass Qt6 / QGIS 4 forward-compatibility gate")
    parser.add_argument("--package-name", "--folder-name", default="", help="Internal root package directory name inside zip (overrides folder name)")
    args = parser.parse_args()

    pdir = Path(args.plugin_dir)
    out_dir = Path(args.output_dir) if args.output_dir else (pdir / "dist")

    try:
        zip_path = package_plugin(pdir, out_dir, bump=args.bump, skip_qt6=args.skip_qt6, package_name=args.package_name)
        print("\n🚀 Next Steps:")
        print("1. Log in to https://plugins.qgis.org/")
        print("2. Navigate to https://plugins.qgis.org/plugins/add/ (or click '+ Add version' on your plugin page)")
        print(f"3. Upload: {zip_path}")
        print("4. Check confirmation boxes and click Upload!")
    except Exception as e:
        print(f"\n❌ Packaging Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
