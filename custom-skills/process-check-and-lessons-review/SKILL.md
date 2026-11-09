# Process Check & Lessons Review — changes get verified, lessons get re-read

Standing rules (Will, 2026-11-08): "whenever we change process, run a check to ensure that it sticks" and "in 1% of my posts, take time to review lessons.phext to ensure that workflow behaviors are working properly." A process change that lives only in the message where it was announced is a defect; a lesson recorded but not lived is the failure this skill exists to catch.

## Rule 1 — every process change gets a sticking check

When a process changes — a standing rule added or amended, a skill created or edited, a cron created or retimed, a workflow redefined — the change is not done when it is written down. In the same session, after the change lands:

1. **Presence** — the rule/skill/cron exists where it belongs: grep the file, read the saved cron definition back (`cron.view`), or run the relevant builder's `--check` (skills.phext, tasks.phext, lessons.phext must print CURRENT).
2. **Machinery** — whatever enacts the change actually exists and runs: the script is executable, the builder passes, the cron is enabled with the intended schedule.
3. **First occasion** — where the change has an immediate occasion (a draw to make, a first run, a first use), perform it now and confirm the behavior matches the intent.

Report the check's result in the plain summary to Will — what was verified, not the receipts (receipts live in the records). A check that fails is repaired in the same session or reported as a failure, never silently carried.

## Rule 2 — 1% of Will's posts trigger a lessons review

- **Trigger**: a daily verification job (`lessons-review-draw`, ~07:40 America/Chicago) counts Will's posts from the previous day across the chats and draws for each one (SHA-256 of a per-post seed, mod 100; a hit at 1). If any post hits, the review runs that morning; otherwise the job stays silent. Counting and drawing happen in the job because a per-message draw cannot be guaranteed inside a live conversation.
- **The review** (when triggered):
  1. Read `~/workspace/phext/lessons.phext` (source of truth: `lessons-source.phext`; rebuild check first — `python3 ~/workspace/phext/build_lessons_phext.py --check` must print CURRENT).
  2. Pick out the lessons that encode checkable workflow behaviors — standing rules with a machine or a habit behind them (publishing discipline, register discipline, verification rules, queue rules).
  3. Check each against the live record: cron definitions and recent runs, builder `--check` outputs, recent dated memory notes, the register, the publish log. Verify from primary sources, never from prose claims.
  4. Report to Will in plain terms: which behaviors are working, which are drifting, and what the drift is. No state pointers in the summary; the detail lives in the run's notes.
  5. A drift is a defect: repair it if the repair is agent-actionable, or record it where it will be seen (register or goal timeline) if it needs Will.
- **Cadence honesty**: the draw is probabilistic — about one post in a hundred, so reviews land roughly every week or two at Will's usual posting rate, sometimes sooner, sometimes later. Never fake a review on a non-hit, and never skip one on a hit.

## Records

- Both rules are lessons in lessons.phext (appended 2026-11-08 to `~/workspace/phext/lessons-source.phext`, rebuilt same session).
- The draw counter and last-review date live with the cron's goal workspace bookkeeping, never in a user-facing document.
- When this skill is created or edited, the closing step of distill-process-to-skill applies: rebuild skills.phext and `--check` CURRENT in the same session, and publish to emise-tools.
