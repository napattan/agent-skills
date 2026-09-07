---
name: update-doc
description: >
  Synchronize documentation after a system, API, schema, metric, or public-claim change.
  Use when the user runs /update-doc, /doc-sync, /audit-docs, /verify-docs, or asks to sync docs
  across markdown and HTML without leaving stale claims.
  Do NOT use for publishing packages, secret scans, or creating new skills
  (use /publish-audit, /publish-qgis, /create-skill).
---

# `/update-doc` (portable)

Cross-document sync for **whatever repo is open now**. Discover the change from **this chat**, then scan **markdown and HTML in the current workspace**. Do not assume thesis filenames, layer counts, or one author's portfolio paths.

---

## 1. Anti-lazy invariant (scoped)

The task is incomplete until every file **in the relation set** is updated or explicitly marked current.

The relation set is **not the whole disk**. It is files that share the changed symbols, numbers, status words, or links. Out-of-scope hits: say "verified, not rewritten."

---

## 2. Public claim vocabulary

Use these words in public docs unless the user's project defines others:

| Word | Meaning |
|:---|:---|
| **LIVE** | A stranger can use it now (install, URL, or download works). |
| **REGISTERED** | Listed somewhere; a public version or install may still be pending. |
| **PREPARED** | Built locally; not a public product page yet. |
| **IN PIPELINE** | Intended next; not released. |
| **DRAFT** | Internal only. |

Do not write LIVE, Published, or 1-click install without a checkable receipt (URL, version table, or installer). `/publish-audit` may **advise** on those words; this skill **owns** the vocabulary.

User-facing/release copy: no em/en dashes (hyphen `-` is fine). No LaTeX. Unicode `→` `×` `≤` is fine. ASCII boxes allowed only inside skill files, not in the user's docs (use Mermaid or tables there).

---

## 3. SOP (every run)

### Step 1: Delta from this chat

From the current conversation, write:

1. What changed (symbols, numbers, paths, statuses).
2. Canonical source (test, live URL, schema, user lock).
3. Deprecated terms that must hit **zero** in the relation set.

If the chat is thin, ask once. Do not invent a project-specific file list.

### Step 2: Scan the current workspace

Search markdown and HTML, including hidden skill/config dirs when the host allows, excluding `.git` and `node_modules`.

Use whatever search exists:

- Host `grep` / `rg --hidden` if present
- PowerShell `Select-String`
- Do not require `rg`

Follow **relations**: same identifiers, metrics, status phrases, and relative links (`../`). In HTML, search core keywords; entities and tags can split phrases.

### Step 3: 5-tier matrix for **this** repo

Classify each hit. Names below are types, not required filenames.

| Tier | Kind |
|:---|:---|
| 1 | In-code contracts (docstrings, types, route comments) |
| 2 | Module README / schema / local spec |
| 3 | Pipeline / handshake docs |
| 4 | Architecture, roadmap, master plan |
| 5 | Public README, changelog, portfolio, profile, release notes |

Show a table: tier, file, sections.

### Step 4: Inner-to-outer sync

Update 1-2, then 3, then 4, then 5. GFM tables with outer pipes. Mermaid for flows in user docs.

If a markdown SSOT has a documented export command in **that repo** (for example a PDF exporter next to the file), run it. Do not assume a path from another project.

### Step 5: Zero-stale check

Re-search deprecated terms in the relation set: **zero hits**. Optional: if the **user's workspace** has `scripts/audit_docs.py` (or the path they name), run it. Do not ship or require a bundled project auditor.

---

## 4. Archetypes (adapt; do not lock files)

Use as hints when the delta matches that domain: simulation solvers, web/API/dashboards, embedded/IoT, spatial/GIS. Fill the matrix from **this** tree, not from examples in this skill.

---

## 5. Rubric

- [ ] Chat delta written (changed / canonical / deprecated)
- [ ] Workspace md/html scanned with the host's search
- [ ] Relation set + 5-tier table shown
- [ ] Inner-to-outer edits; out-of-scope marked
- [ ] Public claims use the vocabulary above
- [ ] Deprecated terms: zero hits in the relation set
