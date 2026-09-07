# -*- coding: utf-8 -*-
"""
Universal Package & Release Pre-Flight Audit Engine.
Performs secret, privacy, security, quality, and platform-specific audits
prior to releasing to GitHub, QGIS, or Food4Rhino.
"""

import sys
import os
import re
import ast
import json
import argparse
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
    ("GitHub Personal Access Token", re.compile(r"\b(ghp_[0-9a-zA-Z]{36}|gho_[0-9a-zA-Z]{36}|github_pat_[0-9a-zA-Z_]{82})\b")),
    ("OpenAI API Key", re.compile(r"\b(sk-[a-zA-Z0-9]{20,}|sk-proj-[a-zA-Z0-9_\-]{20,})\b")),
    ("Anthropic API Key", re.compile(r"\bsk-ant-[a-zA-Z0-9\-_]{20,}\b")),
    ("Google API Key", re.compile(r"\b(AIza[0-9A-Za-z\-_]{35})\b")),
    ("Slack API Token", re.compile(r"\b(xox[baprs]-[0-9a-zA-Z]{10,48})\b")),
    ("RSA/SSH Private Key", re.compile(r"-----BEGIN (?:RSA|OPENSSH|DSA|EC|PGP) PRIVATE KEY-----")),
    ("Database Connection String", re.compile(r"(?i)\b(?:postgres|postgresql|mysql|mongodb\+srv):\/\/[^:\s]+:[^@\s]+@[^\s/]+")),
    (
        "Generic Secret Assignment",
        re.compile(r"(?i)\b(api[_-]?key|secret[_-]?key|auth[_-]?token|bearer[_-]?token|private[_-]?key|db[_-]?password|client[_-]?secret)\s*[:=]\s*[\"']([a-zA-Z0-9_\-\.]{12,})[\"']")
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

EXCLUDED_PATH_ALLOWLIST = {"<user>", "<username>", "<your_username>", "users/default", "default/python/plugins"}

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
                # Mask matched secret for safe reporting
                matched_val = match.group(0)
                masked = matched_val[:4] + "..." + matched_val[-4:] if len(matched_val) > 8 else "***"
                result.add_blocking(f"Potential {label} detected: `{masked}`", str(path), idx)

        # 2. Check Hardcoded Machine Paths
        for label, pat in PATH_PATTERNS:
            match = pat.search(clean_line)
            if match:
                matched_path = match.group(1).lower()
                if not any(allowed in matched_path for allowed in EXCLUDED_PATH_ALLOWLIST):
                    result.add_blocking(f"Hardcoded absolute machine user path ({label}): `{match.group(1)}`", str(path), idx)


def audit_python_ast(path: Path, result: AuditResult):
    """Parse Python AST to detect dangerous security calls and broad exception passes."""
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as e:
        result.add_blocking(f"Python SyntaxError: {e.msg}", str(path), e.lineno or 0)
        return

    lines = source.splitlines()

    class SecurityVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            # Check eval / exec / compile
            if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile"}:
                result.add_blocking(f"Dangerous dynamic code execution call: `{node.func.id}()`", str(path), node.lineno)

            # Check os.system
            if isinstance(node.func, ast.Attribute) and node.func.attr == "system":
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                    result.add_blocking("Insecure `os.system()` invocation. Use parameterized `subprocess.run(..., shell=False)`", str(path), node.lineno)

            # Check subprocess shell=True
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"Popen", "run", "call", "check_call", "check_output"}:
                for kw in node.keywords:
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        result.add_blocking("Subprocess execution with `shell=True` (Shell Injection risk)", str(path), node.lineno)

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
                        result.add_warning("Broad `except Exception: pass` without `# nosec B110` or logging", str(path), node.lineno)

            self.generic_visit(node)

    visitor = SecurityVisitor()
    visitor.visit(tree)


def audit_qgis_metadata(path: Path, result: AuditResult):
    """Audit QGIS metadata.txt for interpolation syntax, required fields, and versions."""
    if not path.exists():
        result.add_blocking("Missing mandatory `metadata.txt` for QGIS plugin", str(path))
        return

    content = path.read_text(encoding="utf-8", errors="ignore")

    # Critical check: raw unescaped '%' causes configparser InterpolationSyntaxError
    for line_no, line in enumerate(content.splitlines(), 1):
        if "%" in line:
            # Check if it has unescaped % (not %%)
            unescaped = re.search(r"(?<!%)%(?!%)", line)
            if unescaped and not line.strip().startswith("#"):
                result.add_blocking(
                    "Unescaped `%` character in metadata.txt will cause QGIS server `InterpolationSyntaxError`. Use `percent` or `%%`",
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


def run_audit(target_dir: str, platform: str = "generic") -> AuditResult:
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
        # Ignore .git and __pycache__ from deep walk
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
    overclaim = re.compile(
        r"(?i)\b(published|1-click install|status:\s*live)\b"
    )
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

    # 4. Platform-Specific Checks
    if platform.lower() == "qgis":
        meta_file = target / "metadata.txt"
        audit_qgis_metadata(meta_file, result)

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

    # 5. License & README
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
    parser.add_argument("--platform", choices=["generic", "qgis", "food4rhino", "github"], default="generic", help="Platform profile to evaluate against")
    args = parser.parse_args()

    res = run_audit(args.target, platform=args.platform)

    print("=" * 70)
    print("PRE-FLIGHT AUDIT")
    print("=" * 70)
    print(f"Target:    {args.target}")
    print(f"Platform:  {args.platform}")
    print(f"Files:     {res.files_scanned}")
    print(f"Blocking:  {len(res.blocking_errors)}")
    print(f"Advisory:  {len(res.warnings)}")
    print("-" * 70)

    if res.blocking_errors:
        print("\nBLOCKING (must fix before publishing):")
        for err in res.blocking_errors:
            print(f"  x {err}")

    if res.warnings:
        print("\nADVISORY:")
        for warn in res.warnings:
            print(f"  - {warn}")

    if res.passed and not res.blocking_errors:
        print("\nVERDICT: PASS (safe to publish for this platform)")
        sys.exit(0)
    else:
        print("\nVERDICT: FAIL (resolve blocking errors before publishing)")
        sys.exit(1)


if __name__ == "__main__":
    main()
