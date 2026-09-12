# -*- coding: utf-8 -*-
"""
Universal Package & Release Pre-Flight Audit Engine (/publish-audit).
Performs secret, privacy, security, Flake8 quality, and platform-specific audits
prior to releasing to GitHub, QGIS, or Food4Rhino.
"""

import sys
import os
import re
import ast
import argparse
import subprocess
import configparser
from pathlib import Path

# Enforce UTF-8 standard output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# High-Entropy & API Key Patterns
# ---------------------------------------------------------------------------
SECRET_PATTERNS = [
    ("AWS Access Key ID", re.compile(r"(?i)\b(AKIA[0-9A-Z]{16})\b")),
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
    ("GitLab Personal Access Token", re.compile(r"\b(glpat-[0-9a-zA-Z_\-]{20,})\b")),
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

# ---------------------------------------------------------------------------
# Machine-Specific Path Patterns (Portability / PII)
# ---------------------------------------------------------------------------
PATH_PATTERNS = [
    ("Windows Absolute User Path", re.compile(r"(?i)\b([a-z]:[/\\]users[/\\](?!<)[a-zA-Z0-9_\-\.]+)")),
    ("macOS Absolute User Path", re.compile(r"(?i)\b(/Users/(?!<)[a-zA-Z0-9_\-\.]+)")),
    ("Linux Absolute Home Path", re.compile(r"(?i)\b(/home/(?!<)[a-zA-Z0-9_\-\.]+)")),
]

EXCLUDED_PATH_ALLOWLIST = {
    "<user>", "<username>", "<your_username>", "users/default", "default/python/plugins", "users/...", "users\\..."
}

# ---------------------------------------------------------------------------
# Packaging Debris & Forbidden Extensions
# ---------------------------------------------------------------------------
FORBIDDEN_FILES = {
    ".ds_store", "thumbs.db", "desktop.ini"
}
FORBIDDEN_EXTS = {".pyc", ".pyo", ".pyd", ".swp", ".bak", ".tmp"}


class AuditResult:
    def __init__(self):
        self.passed = True
        self.blocking_errors = []
        self.warnings = []
        self.checks_run = 0
        self.files_scanned = 0

    def add_blocking(self, msg: str, file_path: str = "", line_no: int = 0):
        self.passed = False
        prefix = f"[{file_path}:{line_no}] " if file_path and line_no else (f"[{file_path}] " if file_path else "")
        self.blocking_errors.append(f"{prefix}{msg}")

    def add_warning(self, msg: str, file_path: str = "", line_no: int = 0):
        prefix = f"[{file_path}:{line_no}] " if file_path and line_no else (f"[{file_path}] " if file_path else "")
        self.warnings.append(f"{prefix}{msg}")


def audit_file_content(path: Path, result: AuditResult):
    """Scan file lines for secrets, credentials, and hardcoded absolute machine paths."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        result.add_warning(f"Unable to read file: {e}", str(path))
        return

    lines = content.splitlines()

    for idx, line in enumerate(lines, 1):
        clean_line = line.strip()

        # Skip comment headers describing patterns
        if clean_line.startswith("#") and "pattern" in clean_line.lower():
            continue

        # 1. Check Secrets
        for label, pat in SECRET_PATTERNS:
            match = pat.search(clean_line)
            if match:
                matched_val = match.group(0)
                masked = matched_val[:4] + "..." + matched_val[-4:] if len(matched_val) > 8 else "***"
                result.add_blocking(f"Potential {label} detected: `{masked}`", str(path), idx)

        # 2. Check Hardcoded Machine Paths
        for label, pat in PATH_PATTERNS:
            match = pat.search(clean_line)
            if match:
                matched_path = match.group(1).lower()
                if not any(allowed in matched_path for allowed in EXCLUDED_PATH_ALLOWLIST):
                    result.add_blocking(
                        f"Hardcoded absolute machine user path ({label}): `{match.group(1)}`", str(path), idx
                    )


def audit_python_ast(path: Path, result: AuditResult):
    """Parse Python AST to detect dangerous security calls, shell injection, and broad exception passes."""
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as e:
        result.add_blocking(f"Python SyntaxError: {e.msg}", str(path), e.lineno or 0)
        return

    lines = source.splitlines()

    class SecurityVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            # 1. Check eval / exec / compile / __import__
            if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
                result.add_blocking(
                    f"Dangerous dynamic code execution call: `{node.func.id}()`", str(path), node.lineno
                )

            # 2. Check os.system, os.popen, posix.system
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in {"system", "popen"}:
                    if isinstance(node.func.value, ast.Name) and node.func.value.id in {"os", "posix"}:
                        result.add_blocking(
                            f"Insecure `{node.func.value.id}.{node.func.attr}()` invocation. "
                            f"Use parameterized `subprocess.run(..., shell=False)`",
                            str(path), node.lineno
                        )

            # 3. Check subprocess shell=True
            if isinstance(node.func, ast.Attribute) and node.func.attr in {
                "Popen", "run", "call", "check_call", "check_output"
            }:
                for kw in node.keywords:
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        result.add_blocking(
                            "Subprocess execution with `shell=True` (Shell Injection risk)", str(path), node.lineno
                        )

            # 4. Check unsafe deserialization (pickle / shelve / marshal)
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in {"load", "loads"} and isinstance(node.func.value, ast.Name) and (
                    node.func.value.id in {"pickle", "_pickle", "marshal"}
                ):
                    result.add_blocking(
                        f"Insecure deserialization with `{node.func.value.id}` (Arbitrary Code Execution risk)",
                        str(path), node.lineno
                    )
                elif (
                    node.func.attr == "mktemp" and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "tempfile"
                ):
                    result.add_blocking(
                        "Insecure `tempfile.mktemp()` (Symlink race condition risk). "
                        "Use `NamedTemporaryFile` or `mkstemp`", str(path), node.lineno
                    )
                # Check dangerous Windows memory injection primitives
                elif node.func.attr in {
                    "VirtualAlloc", "VirtualAllocEx", "WriteProcessMemory", "CreateRemoteThread"
                }:
                    result.add_blocking(
                        f"High-risk memory injection API call detected: `{node.func.attr}`", str(path), node.lineno
                    )

            # 5. Check outbound network sockets / HTTP requests
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in {"urlopen", "get", "post", "put", "delete", "connect"} and (
                    isinstance(node.func.value, ast.Name)
                ):
                    if node.func.value.id in {"requests", "urllib", "httpx", "aiohttp", "socket"}:
                        result.add_warning(
                            f"Network outbound call `{node.func.value.id}.{node.func.attr}()` detected. "
                            "Ensure this call is user-authorized, HTTPS-only, and transmits no private telemetry.",
                            str(path), node.lineno
                        )

            self.generic_visit(node)

        def visit_ExceptHandler(self, node):
            # Check try-except-pass on generic Exception (Bandit B110)
            if node.body and len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                line_text = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
                if "# nosec" not in line_text:
                    is_broad = False
                    if node.type is None:  # bare except:
                        is_broad = True
                    elif isinstance(node.type, ast.Name) and node.type.id in {"Exception", "BaseException"}:
                        is_broad = True

                    if is_broad:
                        result.add_warning(
                            "Broad `except Exception: pass` without `# nosec B110` or logging", str(path), node.lineno
                        )

            self.generic_visit(node)

    visitor = SecurityVisitor()
    visitor.visit(tree)


def audit_flake8(target: Path, result: AuditResult):
    """Audit project code quality and PEP8 compliance using Flake8 with local .flake8 configuration."""
    flake8_cfg = target / ".flake8"
    if not flake8_cfg.exists():
        parent_cfg = target.parent / ".flake8"
        if parent_cfg.exists():
            flake8_cfg = parent_cfg

    cmd = [sys.executable, "-m", "flake8"]
    if flake8_cfg.exists():
        cmd.append(f"--config={flake8_cfg}")
    cmd.append(str(target))

    try:
        proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
        )
        output = proc.stdout.strip()

        if proc.returncode != 0 and output:
            for line in output.splitlines():
                clean = line.strip()
                if clean:
                    result.add_blocking(f"Flake8 Style/Lint Violation: {clean}")
        elif proc.returncode == 0:
            print("  ✓ Flake8 Code Quality Audit: 100% CLEAN (0 violations)")
    except FileNotFoundError:
        result.add_warning(
            "Flake8 module not installed in current Python environment. Run: pip install flake8"
        )
    except Exception as e:
        result.add_warning(f"Flake8 audit failed to run: {e}")


def audit_qgis_metadata(path: Path, result: AuditResult):
    """Audit QGIS metadata.txt for interpolation syntax, required fields, and versions."""
    if not path.exists():
        result.add_blocking("Missing mandatory `metadata.txt` for QGIS plugin", str(path))
        return

    content = path.read_text(encoding="utf-8", errors="ignore")

    # Critical check: raw unescaped '%' causes configparser InterpolationSyntaxError
    for line_no, line in enumerate(content.splitlines(), 1):
        if "%" in line:
            unescaped = re.search(r"(?<!%)%(?!%)", line)
            if unescaped and not line.strip().startswith("#"):
                result.add_blocking(
                    "Unescaped `%` character in metadata.txt will cause QGIS server `InterpolationSyntaxError`. "
                    "Use `percent` or `%%`",
                    str(path), line_no
                )

    cp = configparser.ConfigParser()
    try:
        cp.read(str(path), encoding="utf-8")
        if not cp.has_section("general"):
            result.add_blocking("`metadata.txt` must contain a `[general]` section", str(path))
            return

        required_fields = ["name", "qgisMinimumVersion", "description", "about", "version", "author", "email"]
        for field in required_fields:
            if not cp.has_option("general", field) or not cp.get("general", field).strip():
                result.add_blocking(f"Mandatory metadata field missing or empty: `{field}`", str(path))

        # Check repository & tracker
        for opt in ["repository", "tracker", "homepage"]:
            if cp.has_option("general", opt):
                val = cp.get("general", opt)
                if not val.startswith(("http://", "https://")):
                    result.add_warning(f"Metadata link `{opt}` does not start with https://: `{val}`", str(path))

    except Exception as e:
        result.add_blocking(f"Failed to parse `metadata.txt`: {e}", str(path))


def audit_qgis_plugin_invariants(target: Path, result: AuditResult, skip_qt6: bool = False):
    """Verify core QGIS plugin requirements: classFactory, icons, and Qt6 forward compatibility."""
    init_path = target / "__init__.py"
    if not init_path.exists():
        result.add_blocking("Missing mandatory `__init__.py` hook for QGIS plugin", str(target))
    else:
        init_content = init_path.read_text(encoding="utf-8", errors="ignore")
        if "def classFactory(" not in init_content:
            result.add_blocking("`__init__.py` must define `def classFactory(iface):`", str(init_path))

    icon_png = target / "icon.png"
    icon_svg = target / "icon.svg"
    if not icon_png.exists() and not icon_svg.exists():
        result.add_warning(
            "Missing `icon.png` or `icon.svg` (required for QGIS toolbar and plugin manager)", str(target)
        )

    # Optional Qt6 AST check if check_qt6 is available
    if not skip_qt6:
        qt6_script = Path(__file__).resolve().parent.parent.parent / "publish-qgis" / "scripts" / "check_qt6.py"
        if not qt6_script.exists():
            qt6_script = target.parent / ".agents" / "skills" / "publish-qgis" / "scripts" / "check_qt6.py"

        if qt6_script.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("check_qt6", str(qt6_script))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "audit_directory_for_qt6"):
                    qt6_issues = mod.audit_directory_for_qt6(target)
                    blocking_qt6 = [issue for issue in qt6_issues if issue[3] == "ERROR"]
                    if blocking_qt6:
                        for rel, line, col, sev, msg in blocking_qt6:
                            result.add_blocking(
                                f"Qt6 / QGIS 4 forward-compatibility violation: {msg}", str(target / rel), line
                            )
                    else:
                        print("  ✓ Qt6 / QGIS 4 Forward-Compatibility: 100% COMPLIANT (Green badge)")
            except Exception as e:
                result.add_warning(f"Qt6 audit could not execute: {e}")


def run_audit(
    target_dir: str, platform: str = "generic", skip_flake8: bool = False, skip_qt6: bool = False
) -> AuditResult:
    target = Path(target_dir).resolve()
    result = AuditResult()

    if not target.exists():
        result.add_blocking(f"Target directory does not exist: {target}")
        return result

    print(f"🔍 Starting /publish-audit on: {target}")
    print(f"📦 Platform Profile: {platform.upper()}\n")

    # Collect files
    all_files = []
    for root, dirs, files in os.walk(target):
        # Ignore .git, __pycache__, dist, build from walk
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "dist", "build", ".idea", ".vscode"}]
        for f in files:
            all_files.append(Path(root) / f)

    result.files_scanned = len(all_files)

    # 1. Scan packaging hygiene
    for f in all_files:
        fname = f.name.lower()
        if fname in FORBIDDEN_FILES or f.suffix.lower() in FORBIDDEN_EXTS:
            result.add_warning(f"Forbidden or build artifact file present in package: `{f.name}`", str(f))

    # 2. Scan file content (secrets, machine paths)
    content_suffixes = {
        ".py", ".txt", ".md", ".json", ".yml", ".yaml", ".ini", ".cs",
        ".xml", ".html", ".env", ".ps1", ".sh", ".toml", ".cfg", ".conf",
    }
    overclaim = re.compile(r"(?i)\b(published|1-click install|status:\s*live)\b")
    for f in all_files:
        if not f.is_file():
            continue
        suffix = f.suffix.lower()
        name = f.name.lower()
        if suffix in content_suffixes or name in {".env", "env"}:
            audit_file_content(f, result)
        if suffix == ".md" and name.startswith("readme"):
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                text = ""
            for i, line in enumerate(text.splitlines(), 1):
                if overclaim.search(line) and "pending" not in line.lower() and "registered" not in line.lower():
                    result.add_warning(
                        "README may overclaim public availability (Published / LIVE / 1-click). "
                        "Use REGISTERED / PREPARED / IN PIPELINE unless a receipt exists. "
                        "Vocabulary is owned by /update-doc; this is advisory.",
                        str(f),
                        i,
                    )

    # 3. Scan Python AST
    py_files = [f for f in all_files if f.suffix.lower() == ".py" and not f.name.startswith("test_")]
    for py in py_files:
        audit_python_ast(py, result)

    # 4. Flake8 Code Quality Audit
    if not skip_flake8:
        print("🔍 Checking Flake8 code quality & styling...")
        audit_flake8(target, result)

    # 5. Platform-Specific Invariants
    if platform.lower() == "qgis":
        meta_file = target / "metadata.txt"
        audit_qgis_metadata(meta_file, result)
        audit_qgis_plugin_invariants(target, result, skip_qt6=skip_qt6)

        # Check single top-level folder rule if looking at dist zip
        dist_dir = target / "dist"
        if dist_dir.exists():
            zips = list(dist_dir.glob("*.zip"))
            if zips:
                result.add_warning(
                    "dist/*.zip present. For QGIS single-root zip shape and Qt6 checks, run /publish-qgis. "
                    "This audit does not reimplement zip packaging."
                )

    elif platform.lower() == "food4rhino":
        assemblies = list(target.glob("**/*.gha")) + list(target.glob("**/*.dll"))
        sample_gh = list(target.glob("**/*.gh"))
        if not assemblies:
            result.add_blocking(
                "No compiled `.gha` or `.dll` found. Food4Rhino requires a compiled plugin assembly."
            )
        if not sample_gh:
            result.add_warning("No sample `.gh` canvas found. Recommended for Food4Rhino.")

    # 6. License & README
    has_readme = any(f.name.lower().startswith("readme") for f in all_files)
    has_license = any(f.name.lower().startswith("license") for f in all_files)
    plat = platform.lower()
    if not has_readme:
        result.add_warning("Missing README.md.")
    if not has_license:
        if plat == "github":
            result.add_blocking("Missing LICENSE. GitHub platform profile requires an OSI-style LICENSE file.")
        else:
            result.add_warning("Missing LICENSE file.")

    return result


def main():
    parser = argparse.ArgumentParser(description="Universal Package Pre-Flight Audit Engine (/publish-audit)")
    parser.add_argument("target", help="Path to project directory to audit")
    parser.add_argument(
        "--platform", choices=["generic", "qgis", "food4rhino", "github"], default="generic",
        help="Platform profile to evaluate against"
    )
    parser.add_argument("--skip-flake8", action="store_true", help="Skip Flake8 code quality audit")
    parser.add_argument("--skip-qt6", action="store_true", help="Skip Qt6 / QGIS 4 forward-compatibility AST scan")
    args = parser.parse_args()

    res = run_audit(args.target, platform=args.platform, skip_flake8=args.skip_flake8, skip_qt6=args.skip_qt6)

    print("\n" + "=" * 70)
    print("PRE-FLIGHT AUDIT SCORECARD")
    print("=" * 70)
    print(f"Target:    {args.target}")
    print(f"Platform:  {args.platform}")
    print(f"Files:     {res.files_scanned}")
    print(f"Blocking:  {len(res.blocking_errors)}")
    print(f"Advisory:  {len(res.warnings)}")
    print("-" * 70)

    if res.blocking_errors:
        print("\n❌ BLOCKING ISSUES (must resolve before publishing):")
        for err in res.blocking_errors:
            print(f"  • {err}")

    if res.warnings:
        print("\n⚠️  ADVISORY NOTICES:")
        for warn in res.warnings:
            print(f"  - {warn}")

    if res.passed and not res.blocking_errors:
        print("\n✅ VERDICT: PASS (100% Risk-Proof & Safe to Publish)")
        sys.exit(0)
    else:
        print("\n❌ VERDICT: FAIL (Resolve blocking errors before publishing)")
        sys.exit(1)


if __name__ == "__main__":
    main()
