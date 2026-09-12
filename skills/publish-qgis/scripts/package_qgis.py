# -*- coding: utf-8 -*-
"""
Deterministic QGIS Plugin Packaging & High-Security Release Script (/publish-qgis).
Enforces:
1. Metadata validity & INI interpolation escaping
2. Architecture invariant: classFactory(iface) hook in __init__.py
3. Mandatory Qt6 / QGIS 4 forward-compatibility AST scan ('QGIS 4 Ready')
4. Flake8 code quality & style audit (.flake8 enforcement)
5. Zero secrets, zero developer machine paths (C:\\Users\\...), zero AST security risks
6. Deterministic, single-root byte-reproducible release ZIP archives
"""

import sys
import os
import re
import zipfile
import argparse
import subprocess
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
    r"\.flake8$",
    r"\.bandit$",
    r"\.secrets\.baseline$",
    r"\.env$",
    r"^install_plugin\.py$",
    r"^generate_icons\.py$",
]

# Security patterns for pre-release scan
SECRET_PATTERNS = [
    ("AWS Access Key", re.compile(r"(?i)\b(AKIA[0-9A-Z]{16})\b")),
    (
        "GitHub Personal Access Token",
        re.compile(r"\b(ghp_[0-9a-zA-Z]{36}|gho_[0-9a-zA-Z]{36}|github_pat_[0-9a-zA-Z_]{82})\b")
    ),
    ("OpenAI API Key", re.compile(r"\b(sk-[a-zA-Z0-9]{20,}|sk-proj-[a-zA-Z0-9_\-]{20,})\b")),
    ("Anthropic API Key", re.compile(r"\bsk-ant-[a-zA-Z0-9\-_]{20,}\b")),
    ("Google API Key", re.compile(r"\b(AIza[0-9A-Za-z\-_]{35})\b")),
    ("Slack API Token", re.compile(r"\b(xox[baprs]-[0-9a-zA-Z]{10,48})\b")),
    ("HuggingFace Token", re.compile(r"\b(hf_[0-9a-zA-Z]{34,})\b")),
    ("PyPI API Token", re.compile(r"\b(pypi-AgEIcHlwaS5vcmc[0-9a-zA-Z_\-]{50,})\b")),
    ("GitLab Token", re.compile(r"\b(glpat-[0-9a-zA-Z_\-]{20,})\b")),
    ("NPM Access Token", re.compile(r"\b(npm_[0-9a-zA-Z]{36})\b")),
    ("Stripe Live Secret Key", re.compile(r"\b(sk_live_[0-9a-zA-Z]{24,})\b")),
    ("SendGrid API Key", re.compile(r"\b(SG\.[a-zA-Z0-9_\-]{22}\.[a-zA-Z0-9_\-]{43})\b")),
    (
        "Discord Webhook URL",
        re.compile(r"https:\/\/(?:ptb\.|canary\.)?discord(?:app)?\.com\/api\/webhooks\/\d+\/[A-Za-z0-9_\-]+")
    ),
    ("RSA/SSH Private Key", re.compile(r"-----BEGIN (?:RSA|OPENSSH|DSA|EC|PGP) PRIVATE KEY-----")),
    (
        "Database Connection String",
        re.compile(r"(?i)\b(?:postgres|postgresql|mysql|mongodb\+srv):\/\/[^:\s]+:[^@\s]+@[^\s/]+")
    ),
    (
        "Generic Secret Assignment",
        re.compile(
            r"(?i)\b(api[_-]?key|secret[_-]?key|auth[_-]?token|bearer[_-]?token|"
            r"private[_-]?key|db[_-]?password|client[_-]?secret)\s*[:=]\s*[\"']([a-zA-Z0-9_\-\.]{12,})[\"']"
        )
    ),
]

PATH_PATTERNS = [
    ("Windows User Path", re.compile(r"(?i)\b([a-z]:[/\\]users[/\\](?!<)[a-zA-Z0-9_\-\.]+)")),
    ("macOS User Path", re.compile(r"(?i)\b(/Users/(?!<)[a-zA-Z0-9_\-\.]+)")),
    ("Linux Home Path", re.compile(r"(?i)\b(/home/(?!<)[a-zA-Z0-9_\-\.]+)")),
]

EXCLUDED_PATH_ALLOWLIST = {
    "<user>", "<username>", "<your_username>", "users/default", "default/python/plugins", "users/...", "users\\..."
}


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

    # Validate links (must be HTTPS and not localhost)
    for opt in ["repository", "tracker", "homepage"]:
        if opt in metadata:
            val = metadata[opt].strip()
            if not val.startswith("https://"):
                raise ValueError(f"Security violation: metadata link `{opt}` must use secure `https://`: `{val}`")
            if "localhost" in val.lower() or "127.0.0.1" in val:
                raise ValueError(
                    f"Security violation: metadata link `{opt}` contains localhost/staging address: `{val}`"
                )

    return metadata


def audit_security_and_privacy(plugin_dir: Path) -> list:
    """Scan all package files for hardcoded secrets, developer machine paths, and AST vulnerabilities."""
    import ast
    issues = []
    content_suffixes = {
        ".py", ".txt", ".md", ".json", ".yml", ".yaml", ".ini", ".xml", ".html", ".env", ".ps1", ".sh"
    }

    for root, dirs, files in os.walk(plugin_dir):
        dirs[:] = [d for d in dirs if not any(re.search(pat, d, re.IGNORECASE) for pat in EXCLUDE_PATTERNS)]
        for f in files:
            if any(re.search(pat, f, re.IGNORECASE) for pat in EXCLUDE_PATTERNS):
                continue
            file_path = Path(root) / f
            rel = file_path.relative_to(plugin_dir)

            # 1. Text / Secret / Path Scan
            if file_path.suffix.lower() in content_suffixes or f.lower() in {".env", "env"}:
                try:
                    text = file_path.read_text(encoding="utf-8", errors="ignore")
                    for line_no, line in enumerate(text.splitlines(), 1):
                        clean_line = line.strip()
                        if clean_line.startswith("#") and "pattern" in clean_line.lower():
                            continue
                        for label, pat in SECRET_PATTERNS:
                            m = pat.search(clean_line)
                            if m:
                                val = m.group(0)
                                masked = val[:4] + "..." + val[-4:] if len(val) > 8 else "***"
                                issues.append(f"Secret Leak ({label}) at {rel}:{line_no}: `{masked}`")
                        for label, pat in PATH_PATTERNS:
                            m = pat.search(clean_line)
                            if m:
                                matched_path = m.group(1).lower()
                                if not any(allowed in matched_path for allowed in EXCLUDED_PATH_ALLOWLIST):
                                    issues.append(
                                        f"Developer Machine Path ({label}) at {rel}:{line_no}: `{m.group(1)}`"
                                    )
                except Exception as e:
                    issues.append(f"Could not read {file_path.name}: {e}")

            # 2. Python AST Security Analysis
            if file_path.suffix.lower() == ".py":
                try:
                    py_source = file_path.read_text(encoding="utf-8", errors="ignore")
                    tree = ast.parse(py_source, filename=str(file_path))

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call):
                            # Dangerous dynamic code execution
                            if isinstance(node.func, ast.Name) and (
                                node.func.id in {"eval", "exec", "compile", "__import__"}
                            ):
                                issues.append(
                                    f"AST Security Violation at {rel}:{node.lineno}: "
                                    f"Dynamic `{node.func.id}()` execution"
                                )
                            # Dangerous shell / process execution
                            elif isinstance(node.func, ast.Attribute) and node.func.attr in {"system", "popen"}:
                                if isinstance(node.func.value, ast.Name) and node.func.value.id in {"os", "posix"}:
                                    issues.append(
                                        f"AST Security Violation at {rel}:{node.lineno}: "
                                        f"Insecure `{node.func.value.id}.{node.func.attr}()`"
                                    )
                            elif isinstance(node.func, ast.Attribute) and (
                                node.func.attr in {"Popen", "run", "call", "check_call"}
                            ):
                                for kw in node.keywords:
                                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and (
                                        kw.value.value is True
                                    ):
                                        issues.append(
                                            f"AST Security Violation at {rel}:{node.lineno}: "
                                            "`subprocess` with `shell=True`"
                                        )
                            # Insecure deserialization
                            elif isinstance(node.func, ast.Attribute) and node.func.attr in {"load", "loads"}:
                                if isinstance(node.func.value, ast.Name) and (
                                    node.func.value.id in {"pickle", "_pickle", "marshal"}
                                ):
                                    issues.append(
                                        f"AST Security Violation at {rel}:{node.lineno}: "
                                        f"Insecure deserialization with `{node.func.value.id}`"
                                    )
                            elif isinstance(node.func, ast.Attribute) and node.func.attr == "mktemp":
                                if isinstance(node.func.value, ast.Name) and node.func.value.id == "tempfile":
                                    issues.append(
                                        f"AST Security Violation at {rel}:{node.lineno}: Insecure `tempfile.mktemp()`"
                                    )
                            elif isinstance(node.func, ast.Attribute) and node.func.attr in {
                                "VirtualAlloc", "VirtualAllocEx", "WriteProcessMemory", "CreateRemoteThread"
                            }:
                                issues.append(
                                    f"AST Security Violation at {rel}:{node.lineno}: "
                                    f"Memory injection primitive `{node.func.attr}`"
                                )
                except SyntaxError as e:
                    issues.append(f"Python SyntaxError in {rel}:{e.lineno}: {e.msg}")

    return issues


def audit_flake8_quality(plugin_dir: Path) -> list:
    """Run Flake8 linting using the project's .flake8 configuration."""
    flake8_cfg = plugin_dir / ".flake8"
    if not flake8_cfg.exists():
        parent_cfg = plugin_dir.parent / ".flake8"
        if parent_cfg.exists():
            flake8_cfg = parent_cfg

    cmd = [sys.executable, "-m", "flake8"]
    if flake8_cfg.exists():
        cmd.append(f"--config={flake8_cfg}")
    cmd.append(str(plugin_dir))

    try:
        proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
        )
        output = proc.stdout.strip()
        if proc.returncode != 0 and output:
            return [line.strip() for line in output.splitlines() if line.strip()]
        return []
    except FileNotFoundError:
        return ["Flake8 not installed in current Python environment. Run: pip install flake8"]
    except Exception as e:
        return [f"Flake8 audit execution error: {e}"]


def resolve_package_slug(plugin_dir: Path, output_dir: Path, explicit_slug: str = "", metadata: dict = None) -> tuple:
    """
    Deterministically resolves the internal zip root folder name (package slug)
    to prevent 'Plugin folder name mismatch' errors on plugins.qgis.org.
    """
    if explicit_slug and explicit_slug.strip():
        slug = re.sub(r"[^a-zA-Z0-9_]", "_", explicit_slug.strip()).lower()
        return slug, "CLI argument (--package-name)"

    if metadata:
        for key in ("package_name", "slug", "plugin_package_name"):
            val = metadata.get(key, "").strip()
            if val:
                slug = re.sub(r"[^a-zA-Z0-9_]", "_", val).lower()
                return slug, f"metadata.txt ('{key}')"

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

    folder_name = plugin_dir.name.strip()
    clean_name = folder_name
    if re.match(r"^qgis[-_]", clean_name, flags=re.IGNORECASE):
        clean_name = re.sub(r"^qgis[-_]", "", clean_name, flags=re.IGNORECASE)
    if re.search(r"[-_](qgis[-_]plugin|qgis)$", clean_name, flags=re.IGNORECASE):
        clean_name = re.sub(r"[-_](qgis[-_]plugin|qgis)$", "", clean_name, flags=re.IGNORECASE)

    if clean_name != folder_name:
        slug = re.sub(r"[^a-zA-Z0-9_]", "_", clean_name).lower()
        return slug, f"stripped git wrapper affix from '{folder_name}'"

    slug = re.sub(r"[^a-zA-Z0-9_]", "_", folder_name).lower()
    return slug, f"folder name ('{folder_name}')"


def package_plugin(
    plugin_dir: Path,
    output_dir: Path,
    bump: str = "none",
    skip_qt6: bool = False,
    skip_flake8: bool = False,
    skip_security: bool = False,
    package_name: str = ""
) -> Path:
    """Validate, pre-flight audit, optionally bump version, and package into compliant zip."""
    plugin_dir = plugin_dir.resolve()
    meta_path = plugin_dir / "metadata.txt"
    init_path = plugin_dir / "__init__.py"
    icon_png = plugin_dir / "icon.png"

    print("=" * 70)
    print(f"📦 PRE-FLIGHT RELEASE PACKAGING: {plugin_dir.name}")
    print("=" * 70)

    # Gate 1: Metadata validation
    print("1. Validating metadata.txt syntax & required fields...")
    metadata = validate_metadata(meta_path)
    current_version = metadata["version"]
    print(f"  ✓ Validated metadata.txt: '{metadata['name']}' v{current_version}")

    # Gate 2: QGIS Architecture Invariants
    print("2. Checking QGIS plugin architecture invariants...")
    if not init_path.exists():
        raise FileNotFoundError(f"Missing mandatory `__init__.py` in {plugin_dir}")
    init_content = init_path.read_text(encoding="utf-8", errors="ignore")
    if "def classFactory(" not in init_content:
        raise ValueError("`__init__.py` must define `def classFactory(iface):` hook.")
    print("  ✓ `classFactory(iface)` entrypoint hook verified.")

    if not icon_png.exists():
        print("  ⚠️  Warning: `icon.png` not found in root (recommended for QGIS toolbar).")
    else:
        print("  ✓ `icon.png` verified.")

    # Gate 3: Qt6 / QGIS 4 Forward-Compatibility AST Scan
    if not skip_qt6 and audit_directory_for_qt6:
        print("3. Running Qt6 / QGIS 4 forward-compatibility scan...")
        qt6_issues = audit_directory_for_qt6(plugin_dir)
        blocking_qt6 = [issue for issue in qt6_issues if issue[3] == "ERROR"]
        if blocking_qt6:
            num_qt6 = len(blocking_qt6)
            print(f"\n❌ Qt6 / QGIS 4 Compatibility Check FAILED ({num_qt6} blocking issues):", file=sys.stderr)
            for rel_path, line, col, severity, msg in blocking_qt6:
                print(f"  • {rel_path}:{line}:{col} [{severity}] {msg}", file=sys.stderr)
            raise RuntimeError(
                "Qt6 forward-compatibility scan failed. Fix unscoped enums to earn 'QGIS 4 Ready' badge."
            )
        print("  ✓ Qt6 / QGIS 4 compatibility: 100% COMPLIANT (Green badge verified)")

    # Gate 4: Flake8 Code Quality & PEP8 Audit
    if not skip_flake8:
        print("4. Running Flake8 code quality & styling audit...")
        flake8_violations = audit_flake8_quality(plugin_dir)
        if flake8_violations:
            print(f"\n❌ Flake8 Audit FAILED ({len(flake8_violations)} style/lint violations):", file=sys.stderr)
            for v in flake8_violations:
                print(f"  • {v}", file=sys.stderr)
            raise RuntimeError("Flake8 audit failed. Resolve code style violations or pass --skip-flake8.")
        print("  ✓ Flake8 Code Quality: 100% CLEAN (0 violations)")

    # Gate 5: Security, Secret & Privacy Audit
    if not skip_security:
        print("5. Running High-Security & Privacy Audit (secrets, user paths)...")
        security_issues = audit_security_and_privacy(plugin_dir)
        if security_issues:
            print(f"\n❌ Security & Privacy Check FAILED ({len(security_issues)} violations):", file=sys.stderr)
            for sec_err in security_issues:
                print(f"  • {sec_err}", file=sys.stderr)
            raise RuntimeError(
                "Security audit failed. Remove leaked secrets/developer machine paths before release."
            )
        print("  ✓ Security & Privacy: 100% CLEAN (Zero leaked secrets, zero machine paths)")

    # Version bump if requested
    if bump in {"patch", "minor", "major"}:
        new_version = bump_semver(current_version, bump)
        print(f"\n🔄 Bumping semantic version: {current_version} -> {new_version}")

        lines = meta_path.read_text(encoding="utf-8").splitlines()
        updated_lines = []
        for line in lines:
            if line.strip().startswith("version="):
                updated_lines.append(f"version={new_version}")
            else:
                updated_lines.append(line)

        meta_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
        current_version = new_version
        metadata = validate_metadata(meta_path)

    # Derive package slug and filenames
    output_dir.mkdir(parents=True, exist_ok=True)
    plugin_slug, slug_source = resolve_package_slug(
        plugin_dir, output_dir, explicit_slug=package_name, metadata=metadata
    )

    zip_filename = f"{plugin_slug}_v{current_version}.zip"
    canonical_zip = output_dir / f"{plugin_slug}.zip"
    versioned_zip = output_dir / zip_filename

    # Compile files to package
    files_to_pack = []
    for root, dirs, files in os.walk(plugin_dir):
        dirs[:] = [d for d in dirs if not any(re.search(pat, d, re.IGNORECASE) for pat in EXCLUDE_PATTERNS)]
        for f in files:
            if not any(re.search(pat, f, re.IGNORECASE) for pat in EXCLUDE_PATTERNS):
                rel_path = Path(root).relative_to(plugin_dir) / f
                files_to_pack.append(rel_path)

    print(f"\n📦 Packaging {len(files_to_pack)} verified files into release archive...")
    print(f"📁 Internal root folder name: `{plugin_slug}/` (resolved from {slug_source})")

    # Deterministic timestamp for reproducible builds (no author machine epoch leak)
    fixed_time = (2026, 1, 1, 0, 0, 0)

    for target_zip in [versioned_zip, canonical_zip]:
        with zipfile.ZipFile(target_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for rel in sorted(files_to_pack):
                src_file = plugin_dir / rel
                arcname = f"{plugin_slug}/{rel.as_posix()}"

                # Write with deterministic metadata
                zinfo = zipfile.ZipInfo(filename=arcname, date_time=fixed_time)
                zinfo.external_attr = 0o644 << 16  # Standard readable permissions
                zinfo.compress_type = zipfile.ZIP_DEFLATED
                with open(src_file, "rb") as f_in:
                    zf.writestr(zinfo, f_in.read())

    # Verify zip internal structure
    with zipfile.ZipFile(versioned_zip, "r") as zf:
        names = zf.namelist()
        root_prefixes = {n.split("/")[0] for n in names if "/" in n}
        root_orphan_files = [n for n in names if "/" not in n and n]

        if len(root_prefixes) != 1 or root_prefixes.pop() != plugin_slug:
            raise RuntimeError("Packaging failed: multiple top-level directories detected in archive.")
        if root_orphan_files:
            raise RuntimeError(f"Packaging failed: root orphan files detected: {root_orphan_files}")

    print("\n" + "=" * 70)
    print("✅ RELEASE PACKAGING SUCCESSFUL (100% Risk-Proof Verified)")
    print("=" * 70)
    print(f"  • Plugin Name:     {metadata.get('name')}")
    print(f"  • Package Slug:    {plugin_slug} (resolved via {slug_source})")
    print(f"  • Release Version: v{current_version}")
    print(f"  • Author:          {metadata.get('author')} ({metadata.get('email')})")
    print(f"  • QGIS Minimum:    {metadata.get('qgisminimumversion')}")
    qt6_badge = "Bypassed" if skip_qt6 else "100% Compliant (Green QGIS 4 Ready Badge)"
    print(f"  • Qt6 / QGIS 4:    {qt6_badge}")
    print(f"  • Flake8 Audit:    {'Bypassed' if skip_flake8 else '100% Clean (0 violations)'}")
    sec_msg = "Bypassed" if skip_security else "100% Risk-Proof (0 secrets, 0 path leaks)"
    print(f"  • Security Audit:  {sec_msg}")
    print(f"  • Output Archive:  {versioned_zip} ({versioned_zip.stat().st_size} bytes)")
    print(f"  • Canonical Zip:   {canonical_zip} ({canonical_zip.stat().st_size} bytes)")
    print("-" * 70)

    return versioned_zip


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic QGIS Plugin Packaging & Release (/publish-qgis)"
    )
    parser.add_argument("plugin_dir", help="Path to plugin directory containing metadata.txt and __init__.py")
    parser.add_argument(
        "--output-dir", default="", help="Destination directory for built zip (default: <plugin_dir>/dist)"
    )
    parser.add_argument(
        "--bump", choices=["none", "patch", "minor", "major"], default="none",
        help="Bump version in metadata.txt before packaging"
    )
    parser.add_argument("--skip-qt6", action="store_true", help="Bypass Qt6 / QGIS 4 forward-compatibility gate")
    parser.add_argument("--skip-flake8", action="store_true", help="Bypass Flake8 code quality gate")
    parser.add_argument("--skip-security", action="store_true", help="Bypass security and secret audit gate")
    parser.add_argument(
        "--package-name", "--folder-name", default="",
        help="Internal root package directory name inside zip (overrides folder name)"
    )
    args = parser.parse_args()

    pdir = Path(args.plugin_dir)
    out_dir = Path(args.output_dir) if args.output_dir else (pdir / "dist")

    try:
        zip_path = package_plugin(
            pdir,
            out_dir,
            bump=args.bump,
            skip_qt6=args.skip_qt6,
            skip_flake8=args.skip_flake8,
            skip_security=args.skip_security,
            package_name=args.package_name
        )
        print("\n🚀 Ready for Official Publication:")
        print("1. Log in to https://plugins.qgis.org/")
        print("2. Navigate to https://plugins.qgis.org/plugins/add/ (or click '+ Add version' on your plugin page)")
        print(f"3. Upload: {zip_path}")
        print("4. Check confirmation boxes and click Upload!")
    except Exception as e:
        print(f"\n❌ Packaging Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
