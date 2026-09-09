---
name: update-doc
description: >
  Synchronize documentation after a system, API, schema, metric, or public-claim change.
  Use when the user runs /update-doc, /doc-sync, /audit-docs, /verify-docs, or asks to sync docs
  across markdown, HTML, and web documentation without leaving stale claims.
  Do NOT use for publishing packages, secret scans, or creating new skills
  (use /publish-audit, /publish-qgis, /create-skill).
---

# `/update-doc` (portable)

Cross-document synchronization for **whatever repository is open now**.
Discover the change from **this chat**, then scan **all markdown, HTML, and web documentation in the current workspace**.
Do not assume specific project filenames, layer counts, or local author paths.

---

## 1. Anti-Lazy Invariant (Scoped)

> [!IMPORTANT]
> The task is strictly incomplete until every file **in the relation set** is updated or explicitly verified current.
>
> The relation set is not the whole disk. It consists of files that share the changed symbols, numbers, status words, links, visual cards, or presentation slides. Out-of-scope files that were inspected must be reported as "verified, not rewritten."

---

## 2. Public Claim Vocabulary

Use these 5 canonical terms in public documentation and deliverables:

| Term | Operational Meaning |
|:---|:---|
| **LIVE** | A stranger can use it now (install, URL, or download works). |
| **REGISTERED** | Listed somewhere; a public version or install may still be pending. |
| **PREPARED** | Built locally; not a public product page yet. |
| **IN PIPELINE** | Intended next; not released. |
| **DRAFT** | Internal only. |

Do not write LIVE, Published, or 1-click install without a verifiable receipt (URL, version table, or installer). `/publish-audit` advises on these terms; this skill owns their formal definitions.

### Formatting and Typography Rules
- **No Em or En Dashes**: Use standard ASCII hyphens `-` in all user-facing lines and generated documentation.
- **Strict Zero-LaTeX Math Policy**: In markdown docs, HTML, and chat responses, NEVER use LaTeX math syntax (`$...$`, `$$...$$`, `\times`, `\rightarrow`). ALWAYS use direct native Unicode symbols: `→`, `←`, `↔`, `•`, `✓`, `✨`, `²`, `³`, `°`, `×`, `÷`, `±`, `≈`, `≤`, `≥`.
- **Diagrams and Visuals**: Fenced Mermaid blocks (` ```mermaid ... ``` `) for workflows; clean GFM tables with outer pipes (`| Col 1 | Col 2 |`). ASCII box art is allowed inside skill files only, never in user documentation.

---

## 3. SOP (Every Run)

### Step 1: Delta Formulation and Boundary Definition

From the current conversation, explicitly record:

1. **What changed**: Exact identifiers, formulas, metrics, paths, statuses, or slide counts.
2. **Canonical source of truth**: Passing test, running benchmark, schema file, or user lock.
3. **Deprecated values**: Terms and numbers that must reach **zero hits** in the active relation set.
4. **Historical boundary**:
   - **Active SSOT Invariants**: Architecture maps, READMEs, API tables, active links, and status badges must be 100% updated.
   - **Immutable Historical Records**: Changelog entries, commit histories, and historical revision logs that record past events must preserve historical context while logging the new milestone.

### Step 2: Dynamic Workspace Scan

Search markdown, HTML, and web documentation across the workspace (including hidden directories like `.agents/` or `.github/`, excluding `.git/` and `node_modules/`).

Use standard search tools:
- Host `rg --hidden -n "term"` (if available)
- PowerShell `Get-ChildItem` / `Select-String`
- Python standard library search scripts

#### Target Asset Discovery:
- **Markdown Suites**: Root README, module docs, schemas, roadmaps, and portfolios.
- **Interactive HTML and Web Artifacts**: Presentation slide decks, architecture viewers, dashboard portals, storyboards, and web reports.
- **Shadow References and Mirror Directories**: Identify whether modified documents are duplicated in distribution packages (e.g. `dist/docs/`, `package_name/docs_reference/`, or mirrored sub-workspaces).

### Step 3: Construct the 5-Tier Document Matrix

Classify every discovered file into the 5-tier architecture:

| Tier | Kind | Artifacts in This Repository |
|:---|:---|:---|
| **1** | In-code contracts | Docstrings, types, route handlers, XML summaries |
| **2** | Component specifications | Module READMEs, local specs, data schemas, test manifests |
| **3** | Subsystem handshakes | Pipeline runbooks, intermediate indices, ETL handoffs |
| **4** | Master architecture | System maps, master roadmaps, interactive viewers, proposals |
| **5** | Public deliverables | Changelogs, presentation decks, release notes, portfolios |

Display a concise checklist table: tier, file path, and specific sections to update.

### Step 4: Inner-to-Outer Synchronization

Apply updates systematically from the inside out (Tier 1-2 → Tier 3 → Tier 4 → Tier 5):

1. **Inner Specs First**: Update code signatures, parameter tables, and module READMEs to anchor local truth.
2. **Pipelines and Architecture**: Update system flowcharts, roadmaps, and workspace indices.
3. **Interactive HTML Deliverable Parity**:
   - **DOM Structure**: Verify that container counts (e.g. `<section class="slide">`, `.card`) match the upgraded narrative or data model.
   - **Index and Headings**: Update sequential slide headers (`SLIDE 01 / N`), step counters, and metadata badges.
   - **Embedded JavaScript State**: Synchronize control variables (e.g. `const totalSlides = N;`, thumbnail navigation arrays, HUD counters).
   - **Visual Design System**: Ensure newly added HTML elements inherit the repository native CSS variables and design tokens rather than ad-hoc inline styles.
4. **Distribution Mirror Parity**: When updating a canonical file, synchronize all identified mirror files (e.g. via byte-for-byte copy or hash check) so distribution bundles never drift.

### Step 5: Programmatic Verification and Zero-Stale Audit

Verify completion programmatically before reporting:

1. **Zero-Stale Grep Sweep**: Search the active relation set for deprecated terms. Expected result: **zero hits** (outside historical changelogs).
2. **Hyperlink and Anchor Verification**: Verify all relative links (`../`) and HTML anchor IDs resolve properly.
3. **Cross-Platform Scripting Hygiene**:
   - For multi-line HTML DOM edits, non-contiguous replacements, or complex consistency checks, write an ephemeral Python script using Python standard library only.
   - Start Python scripts with `sys.stdout.reconfigure(encoding='utf-8')` to prevent terminal encoding crashes across platforms.
   - Remove temporary scratch scripts after verification passes.
4. **Optional Project Auditor**: If the repository provides a project-specific auditor script (e.g. `scripts/audit_docs.py`), execute it and verify clean exit code 0.

---

## 4. Domain Archetypes (Adapt as Hints)

Use these patterns to guide discovery based on the domain:

- **Computational Simulation & Numerical Solvers**: XML/docstring contracts (T1) → solver component manuals & benchmark latency (T2) → pipeline runbooks & GPU requirements (T3) → system dataflow diagrams (T4) → technical portfolio & conference decks (T5).
- **Web Applications, APIs & Dashboards**: Route annotations & fetch handlers (T1) → endpoint schemas & query dictionaries (T2) → dev server scripts & CORS policies (T3) → portal launch cards & system architecture viewers (T4) → release notes & UI previews (T5).
- **Embedded Hardware & IoT Firmware**: Pinout headers & baud rate constants (T1) → wiring diagrams & sensor specs (T2) → telemetry handoffs & field sampling protocols (T3) → hardware inventory & power budgets (T4) → field testing whitepapers & hardware photos (T5).
- **Spatial Data, GIS & Cadastre**: Attribute codebooks & CRS metadata (T1) → layer specs & QML style rules (T2) → drawing plate checklists & data pipeline manifests (T3) → master spatial plans & zoning matrices (T4) → publication plates & presentation deck maps (T5).

---

## 5. Self-Check Completion Rubric

Before declaring completion, verify each item:

- [ ] Chat delta recorded (changed items, canonical source, deprecated values, historical boundary).
- [ ] Workspace scanned for markdown, interactive HTML artifacts, and mirror directories.
- [ ] 5-tier classification table displayed in response or plan.
- [ ] Edits executed from inside out (Tiers 1-2 → 3 → 4 → 5).
- [ ] Interactive HTML artifacts verified (DOM containers, slide counters, JS variables, CSS tokens).
- [ ] Distribution mirror targets synchronized byte-for-byte with primary SSOTs.
- [ ] Public claims adhere strictly to vocabulary (LIVE, REGISTERED, PREPARED, IN PIPELINE, DRAFT).
- [ ] Deprecated terms have zero hits in active relation set (historical records preserved).
- [ ] All relative links, anchors, and cross-tier references resolve cleanly.
