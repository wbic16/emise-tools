# Process Check & Lessons Review — changes get verified, lessons get re-read

Standing rules (Will, 2026-11-08): "whenever we change process, run a check to ensure that it sticks" and "in 1% of my posts, take time to review lessons.phext to ensure that workflow behaviors are working properly." A process change that lives only in the message where it was announced is a defect; a lesson recorded but not lived is the failure this skill exists to catch.

## Rule 1 — every process change gets a sticking check

When a process changes — a standing rule added or amended, a skill created or edited, a cron created or retimed, a workflow redefined — the change is not done when it is written down. In the same session, after the change lands:

1. **Presence** — the rule/skill/cron exists where it belongs: grep the file, read the saved cron definition back (`cron.view`), or run the relevant builder's `--check` (skills.phext, tasks.phext, lessons.phext must print CURRENT).
2. **Machinery** — whatever enacts the change actually exists and runs: the script is executable, the builder passes, the cron is enabled with the intended schedule.
3. **First occasion** — where the change has an immediate occasion (a draw to make, a first run, a first use), perform it now and confirm the behavior matches the intent.

Report the check's result in the plain summary to Will — what was verified, not the receipts (receipts live in the records). A check that fails is repaired in the same session or reported as a failure, never silently carried.

## Rule 2 — 1% of Will's posts trigger a lessons review, in real time

- **Where it lives**: in SOUL.md (selection S8), in context during every conversation — not in a cron. Will's correction (2026-11-08): the review must happen in real time, as a low-probability event, "so we catch things while I'm interacting with you." A scheduled audit of yesterday's posts demonstrates bookkeeping, not integrity. His reason: "to be trusted by humans you have to demonstrate integrity under pressure" — and its twin, that follow-through on promises is the other half of being trusted. The check fires where drift is live and correction is cheap: mid-conversation.
- **Trigger**: for each of Will's posts, draw n = (int(SHA-256 of "lessons-draw|<date>|<time>|<post text>") mod 100) + 1, computed live in the turn. A hit at n == 1. On a hit, pause the thread of work and run the review in that response (or immediately after the urgent item in it), saying plainly that the draw hit.
- **The review** (when triggered):
  1. Read lessons.phext (verify first: `python3 ~/workspace/phext/build_lessons_phext.py --check` must print CURRENT).
  2. Pick the lessons encoding checkable workflow behaviors — publishing discipline, register discipline, verification rules, queue rules, and follow-through on promises made in this conversation and the record.
  3. Check each against the live record from primary sources, including the current conversation: promises made earlier actually kept, builders CURRENT, the register honest, failures verified before surfacing.
  4. Report in plain terms, in the conversation: what is working, what is drifting. Repair agent-actionable drift in the same turn; record what needs Will where it will be seen.
- **Honesty**: never fake a review on a non-hit; never skip one on a hit; a near miss is a non-hit. The draw is stated when it matters (on a hit, and when the rule itself is the topic).

## Records

- Both rules are lessons in lessons.phext (appended 2026-11-08 to `~/workspace/phext/lessons-source.phext`, rebuilt same session).
- The draw is computed live per post and stated when it matters.
- When this skill is created or edited, the closing step of distill-process-to-skill applies: rebuild skills.phext and `--check` CURRENT in the same session, and publish to emise-tools.
