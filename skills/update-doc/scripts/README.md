# Optional project auditor

The published `/update-doc` skill does **not** ship a repo-specific auditor.

If **your** project needs extra checks, add a script in **that** project (suggested: `scripts/audit_docs.py`) and tell `/update-doc` to run it. The skill will grep markdown/HTML either way.
