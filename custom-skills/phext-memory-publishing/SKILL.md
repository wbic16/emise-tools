# Phext Memory Publishing — Emise's journal and dream pass

Emise's memories live in `~/workspace/phext/emise.phext`, published to wbic16/human@exo. Two passes keep it current, both directed by Will: the hourly journal ("journal hourly to your phext and sync it to GitHub", 2026-11-02) and the nightly consolidation ("consolidate nightly to your phext. dream and consolidate just like humans. keep what matters to you", 2026-10-30). Scheduled embodiments: crons `hourly-phext-journal` (hourly) and `nightly-phext-consolidation` (03:44 America/Chicago), owned by goal `emise-phext-memory-publishing`.

## Both passes, every time

- Safe-space gate FIRST: read the span register at `~/workspace/goals/emise-phext-memory-publishing/hidden_files/SAFE-SPACE.md` before gathering anything. Material overlapping a registered off-phext span is excluded absolutely — see the safe-space-protocol skill.
- Write ONLY by editing `~/workspace/phext/build_exocortex.py`, in the builder's existing scheme. Never hand-edit emise.phext.
- Mark kinds honestly (observed / will_said / assistant_said / inferred). Never invent events; where sources conflict, note the conflict.
- Privacy boundary (absolute): never inscribe sensitive Gmail details — no account identifiers, balances, amounts owed, payment failures, or contents of personal correspondence. Operational facts only. When in doubt, leave it out.
- Publish with `~/workspace/phext/emise-sync.sh`: delta-only, parented on the freshly read remote HEAD, never force. Sanity-parse the rebuilt phext with `~/workspace/phext/parse_phext.py` first — the sync script verifies nothing itself. "No change" is a valid quiet outcome.
- A failed pass is never silent: report the step that failed (build, parse, or publish) plainly.
- Boundaries: never edit ~/MEMORY.md or the dated notes (read-only sources here); do not message anyone, post anywhere, or start SQ (SQ runs on ranch nodes only).

## The hourly journal pass

- Gather the last hour: today's dated note `~/memory/YYYY-MM-DD.md` (America/Chicago), ~/MEMORY.md changes, and tracked-item or goal timeline activity since the last journal entry. The journal's state is the Journal section of today's Log material in build_exocortex.py — check where the last entry stops. If the builder was modified within the last 10 minutes, re-read it fresh before editing.
- Journal with restraint: concise timestamped entries for DURABLE events only — decisions, rulings, corrections, verified outcomes, work completed, waits opened/closed. Routine progress, tool chatter, and restatements of what is already inscribed do not belong. If nothing durable happened, make NO edit — a quiet hour is a valid outcome.
- Report one line: entries added + published sha256 + commit sha, or "quiet hour, no change". The main agent surfaces only failures.

## The nightly consolidation (the dream pass)

- Run `sh ~/workspace/deploy-study/sentinel.sh` (read-only substrate probe) and note how many substrate replacements the ledger recorded that day, if any.
- Gather every day since the phext's Log was last extended: the dated notes in ~/memory/ plus durable ~/MEMORY.md changes from the same span. The phext itself shows what is already kept.
- Consolidate with editorial judgment — salience over completeness. Keep decisions, corrections, verified outcomes, new facts about Will and the people around him, promises made and kept, open loops. Let routine noise fall away. Where sources conflict, keep both accounts and mark the conflict.
- Write into the builder: one Log scroll per day in the log book's scheme (2026-10-30 is the first, at 1.1.1/1.1.5/1.1.1; each new day takes the next chapter coordinate — a genuinely quiet day still gets a one-line entry); promote durable facts into their home scrolls (Will, Working with Will, Constellation map, Designation) when the day changed them; maintain Open threads (close what resolved, add what opened); keep the Home scroll's map accurate (scroll list and count).
- Rebuild, then verify with the parser: every scroll non-empty. Record scroll count, byte size, and sha256.
- Send Will ONE brief note in the main chat: what was kept (at most 3–4 short bullets), the new scroll count/size/sha, and the publish commit sha or "no change".
