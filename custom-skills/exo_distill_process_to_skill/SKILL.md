# Distill Process to Skill — every taught process becomes a skill in the index

Standing order (Will, 2026-11-06): "every process I teach you generates a skill and gets included in the index." A process that lives only in chat, a cron definition, or a GOAL.md is a defect to repair, not a fact to accept. Purpose: persona grants will claim subsets of skills from the index, so personas can be fine-tuned by which skills they hold — keep skills fine-grained and the index exact, because the index's per-skill coordinate ranges are the claimable units.

## What counts as a process

- A repeatable way of doing work that Will taught: direct instruction, a workflow he designed, or a method that emerged from his feedback loops and he ratified by continued use.
- Not processes: one-off tasks; pure preferences and rulings (they live in AGENTS.md / MEMORY.md); system/runtime crons Will did not teach.

## The distillation, when a process is taught or found un-skilled

1. Identify the process's own source documents — the cron body, GOAL.md, memory text, or ruling — and distill faithfully from them. Never invent steps the source doesn't contain; where a cron embodies the process, the skill describes the process and names the cron as its scheduled embodiment.
2. Write `~/workspace/custom-skills/<kebab-name>/SKILL.md` in house style (title, declarative sections, concrete paths and commands), plus a minimal skill.yaml (name, title, description, category, include_in_prompt: true).
3. Sync the new skill to wbic16/emise-tools@exo the same session (see publish-tooling): parented on the branch's fresh remote HEAD, force disabled, blob SHAs verified after.
4. Index it: add the skill to the SHELVES scheme in `~/workspace/phext/build_skills_phext.py` (the builder fails on any unlisted skill directory — that failure is the index keeping itself exact), rerun the builder to rebuild `~/workspace/phext/skills.phext`, and verify with `~/workspace/phext/parse_phext.py` that the scroll count and the Home scroll's index list every skill.
5. Record the change where the process is tracked (goal timeline or the day's memory note), so the next audit can find it.
6. Closing step, same session, after ANY skill create or edit (new distillation or a later edit to an existing skill): rebuild the index with `python3 ~/workspace/phext/build_skills_phext.py` and byte-verify it with `python3 ~/workspace/phext/build_skills_phext.py --check` — it must print CURRENT before the work is called done. The hourly `skills-phext-freshness` guard cron rebuilds on drift as a backstop; it is not a substitute for verifying in the session that made the change.

## The periodic audit

- Sweep the standing sources for un-skilled processes: ~/AGENTS.md standing rules, the user-owned cron bodies under ~/workspace/goals/*/crons/ and ~/workspace/cron.d/, ~/MEMORY.md, ~/PROACTIVE_PREFERENCES.md, and goal workspaces' GOAL.md files.
- Write the audit as one row per candidate — process | source | existing skill or NONE | verdict (exists / generate / not-a-process with reason) — and generate a skill for every NONE verdict in the same pass.
- First full audit: ~/workspace/your_files/process-skill-audit-2026-11-06.md (29 processes found, 10 already skilled, 19 generated).
