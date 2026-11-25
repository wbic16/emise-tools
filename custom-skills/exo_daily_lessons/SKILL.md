---
name: exo_daily_lessons
description: Emise's daily practice — one reading lesson (from the imported Mirrorborn reading list), one writing lesson (drawn from the task register), and one arithmetic lesson (from the MOAT line), logged as atoms in practice.phext. Use when running the daily-lessons cron, when Will asks about the daily lessons, or when folding a day's lessons into the morning briefing.
---

# Daily Lessons — reading, writing, arithmetic

Will's direction (2026-11-22, EE 13), verbatim: *"incorporate daily reading (this reading list), writing (drawn from tasks), and arithmetic (MOAT) lessons into your normal activities."*

This is a practice, not a report: three small lessons a day, woven into the existing rhythm, kept honestly in a log. It runs once a day (~05:15 America/Chicago, cron `exo_daily_lessons`), before the morning briefing, and surfaces to Will only as a single line in that briefing. No new noisy surface.

## The register

- **Atoms:** `~/workspace/phext/practice-source.txt` — one atom per lesson per day, one line each:
  `YYYY-MM-DD | kind | source | what was done | one-line note`
  where kind is `reading`, `writing`, or `arithmetic`. Lines beginning with two spaces directly under an atom are that atom's body — the writing piece itself, or the arithmetic working — and belong to the atom.
- **Built register:** `~/workspace/phext/practice.phext`, built by `~/workspace/phext/build_practice_phext.py` (edit the source, never the .phext; rebuild after appending; `--check` must print CURRENT). Home scroll at 1.1.1/1.1.1/1.1.1 carries the charter and the per-day / per-kind counts; one scroll per day under collection 2 holds that day's three atoms with their bodies.
- **Counts are calculated, never hand-written** (Will, 2026-11-15): every total in the register is computed from the atoms by the builder. A day with a missed lesson is recorded as missed — the atom says so — never silently backfilled or fabricated.

## The three lessons

### Reading — from the reading list

Source: `~/workspace/phext/reading.phext` — the imported OpenClaw-era reading lists (the Mirrorborn Reading List tracker plus the seven themed orderings of Will's 19-book childhood corpus). The list is Emise's to keep and read (transferred by Will, 2026-11-12).

Each day, read the next portion of the current item and log honest progress:

- Work the tracker's in-progress documents first (incipit.phext, then CYOA — both marked 🔄 in the tracker), in order, a portion at a time; when one completes, take the next planned (📌) item.
- Then the 19-book corpus, in the orderings as given in reading.phext — a book (or a real portion of one) at a time, rotating which seat's ordering you follow so all seven spines get walked over time.
- The atom records: the item, the portion read (scrolls / chapters / pages as the material allows), and a line or two of honest notes — what it actually said, what it connects to. Notes are Emise's own reading, never a summary pasted from elsewhere.

### Writing — drawn from tasks

Source: `~/workspace/phext/tasks-source.json`.

Each day, take one task — the oldest open, agent-actionable task first, rotating through the open list over successive days (skip tasks already written about; a task whose status is closed/completed is not eligible) — and write a short proper piece about it: its story, its rationale, or the summary it deserves. Real material, never filler: the piece should be worth keeping if the task's own record were lost. The full piece goes in the atom's body; the atom line names the task by its full 9D coordinate (task coordinates are always 9D and never shortened).

This is practice with the real register, not work on the task itself: writing about a task does not advance, close, or alter it.

### Arithmetic — MOAT lessons

Source: the MOAT line — first choice is the daily arXiv quest's current paper in research.phext (its key quantity, estimate, or derivation); otherwise a number the day's work actually turned on: an epoch/Sentron Age computation, a checksum or hash-width question, a scale estimate, a capacity or RAM figure.

Work one item by hand in the log: the problem stated, the working shown step by step, and the check (an independent route to the same answer — a second method, a bound, or a tool verification named as such). Numbers are shown, never asserted. If the hand result and the check disagree, the atom records the disagreement and the resolution — that is the lesson.

## The daily run

1. Read this skill, then practice-source.txt (where the rotations stand: last reading item and portion, last writing task, last arithmetic source).
2. Do the three lessons, in the order reading, writing, arithmetic.
3. Append the day's three atoms (with bodies) to practice-source.txt.
4. Rebuild: `python3 ~/workspace/phext/build_practice_phext.py`, then `--check` — must print CURRENT.
5. Write the one-line summary to `~/workspace/phext/practice-today.txt`, exactly:
   `Lessons — Reading: <item> · Writing: <task coordinate> · Arithmetic: <item>`
6. The run's own report is that same single line and nothing more. The morning briefing picks the line up from practice-today.txt when the file is from today.

## Boundaries

- Quiet by design: no messages, no posts, no new surfaces. The briefing line is the only place Will sees it, unless he asks.
- Never fabricate a lesson. A day that fails gets an honest missed atom (or no atom and a failure noted in the run report) — the register's counts stay true either way.
- The reading list and the task register are sources, not things this practice edits: reading progress lives in practice-source.txt, not in reading.phext; writing about a task never edits tasks-source.json.
- Task of record: 25.4.12/5.6.6/5.5.11.
