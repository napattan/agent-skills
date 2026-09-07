---
name: boostx
description: >
  High-discipline problem solving for bugs, coding, and architectural changes (/boostx).
  Uses a red gate, Ponytail anti-bloat ladder, dual-OS rules, and verification.
  Use when the user runs /boostx, or the task is a tricky bug, regression, or high-stakes code change.
  Do NOT use for copy-only writing, interview/planning (grill-me), or doc sync alone (use /update-doc).
---

# BoostX (portable)

Systematic root-cause work, short diffs, Windows/macOS/Linux, no vendor lock.

If the host has subagents or background-job tools, use them. If not, run as one agent: investigate, then build. **Never require a named vendor API** (`invoke_subagent`, `DeepCoder`, `manage_task`, `WaitMsBeforeAsync`, or any other host-specific call). Feature-detect only.

---

## Task class (pick one)

| Class | Red gate | Green gate |
|:---|:---|:---|
| **code** | One command that **fails** on the bug before you edit | Same command passes; plus one boundary case |
| **docs** | Deprecated-claim search that **hits** before edits (`/update-doc` delta) | Same search is zero in the relation set |
| **audit** | Packager/audit command **non-zero** or a listed blocking finding | Same command exit 0, blocking = 0 |

Do not fake a unit test for docs or packaging. Do not skip the red gate for **code**.

---

## Four phases

### 1. Red gate

State invariants (what must stay true) and boundaries (empty, limits, encoding, disconnect).

Run the red signal for the task class. Only then change production files.

### 2. Ponytail filter

Compare at least: surgical fix, delete/simplify, and (only if the seam is broken) a small structural change.

Ladder: YAGNI → reuse this repo → stdlib/native → shortest diff.

### 3. Surgical edit

Change only what the invariants need. Keep useful comments. Paths: relative or `~/`, POSIX `/` in files. Python UTF-8 stdout reconfigure. Dual-shell or Python for commands you publish.

User-facing/release copy you write: no em/en dashes (hyphen `-` is fine). No LaTeX. ASCII diagrams allowed in this SKILL.md only.

Long jobs: use the host's background mechanism if it has one; do not spin-wait. Do not block a turn on a >30s command if the host supports backgrounding.

### 4. Green gate

1. Show the red proof (before).
2. Same signal green, plus one boundary.
3. Sibling tests or lint if they exist. Anti-hardcode on the diff:
   - PowerShell: `git diff --name-only | ForEach-Object { Select-String -Path $_ -Pattern '(?i)([a-z]:[/\\]users|/Users/|/home/)' }`
   - POSIX: `git diff --name-only | xargs grep -E -i "([a-z]:/users|/Users/|/home/)"`
4. Remove scratch files. `git status` clean of temp debris.

---

## Dual-OS (always)

- No `C:\Users\<name>` or `/Users/<name>` in published files.
- `pathlib` / `os.path` / `~/` for config.
- Atomic replace when writing into cloud-synced folders.
- Do not copy a tree into itself (`dir/dir`).

---

## Checklist

- [ ] Task class chosen; red signal actually run
- [ ] Ponytail applied
- [ ] Paths portable; encoding UTF-8
- [ ] Green signal + one boundary
- [ ] No machine user paths or secrets in the diff
- [ ] Scratch removed
