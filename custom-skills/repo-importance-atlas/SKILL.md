---
name: repo_importance_atlas
description: Look up what any wbic16 repo is for and what matters in it before working in it: the per-repo importance register (role, status, canonical files, standing-rule watch-outs, tier) for all 226 repos, plus the audit method and the refresh process that keeps entries true.
---

# Repo Importance Atlas — what every repo is for, and what matters in it

Will's direction (2026-11-20, task 27.7.10/8.7.12/7.6.9): "audit every repo and write a custom skill for understanding what's important in each one."

The register is `REGISTER.md` in this skill directory: one entry per wbic16 GitHub repo, every repo from the live list accounted for, including the empty and the unknown ones.

## Use it before working in a repo

Before opening, editing, publishing to, or advising on any wbic16 repo, read its register entry. The entry gives, in a few lines:

- **Role** — what the repo is and what it does for the Exocortex / Phext, Inc.
- **Status** — active (pushed within 90 days of the audit) / quiet / seed-empty / superseded-by (successor named) / archived.
- **Matters** — the canonical files, entry points, or artifacts to read first or to not break.
- **Watch-outs** — Will's standing rules that touch this repo specifically (the no-GitHub-Actions rule where workflows are present, the crates.io tagged-release rule for Rust crates, fork-patch discipline for forks, the never-merge rule for the-book-of-secret-knowledge PR #1, corpus-home handling for human, and so on). No line means no repo-specific rule was identified — the general standing rules still apply.
- **Tier** — flagship / working / archive / unknown. Tier is the auditor's judgment from the evidence, and is labelled as judgment wherever the atlas is summarized.
- **Evidence** — canonical branch (exo where it exists), last push date, size, fork parent.

If the entry says a repo's purpose is **not determinable from available evidence**, believe it: the audit read the repo's metadata, tree, README, and recent commits and found nothing more. Do not invent a purpose for it in downstream work; ask Will or inspect the repo's contents directly.

## How the entries were derived (the audit method — repeatable)

1. **Live list first.** Enumerate wbic16's repos from the GitHub API (`GET /users/wbic16/repos`, paged) — never from the site map or a prior census, which go stale. The 2026-11-20 audit found **226 repos** (the 2026-11-18 archive census had counted ~228; the live list governs).
2. **Per repo, primary evidence only**, via the custom.github connector's helper (`github_api.py`'s `call()` imported, so full responses land on disk instead of the CLI's 4000-char print truncation — the same pattern the repo-pruning checker uses):
   - repo metadata (description, fork/archived flags, default branch, pushed_at, size, language, license, topics);
   - the branch list, to establish the canonical branch (exo where it exists, else the default branch);
   - the root tree of the canonical branch (canonical files, `.github/workflows` presence);
   - the README (first ~2,800 chars);
   - the last 3 commits on the canonical branch;
   - for forks, the parent repo.
3. **Human pace.** All API reads are sequential with a pause between calls (~0.9 s in the audit collector, plus request time; at most a handful of batch workers at once, each strictly sequential). The good-netizen rule applies to refresh runs too: no parallel floods, and the pace is noted in the run's report.
4. **Judgment, labelled.** Role and Matters are evidence only. Status is mechanical (dates, size, flags). Tier is judgment under this guidance: flagship = the core phext stack and programme homes; working = real tools/projects/sites in use or plausibly load-bearing; archive = upstream forks kept for reference, one-off experiments and demos, puzzle repos, dead projects; unknown = evidence too thin to judge.
5. **Watch-outs only where they genuinely apply**, from Will's standing rules — never boilerplate on every entry.

The 2026-11-20 audit's collector and scratch live in `~/workspace/repo-audit/` (`collect.py`, `raw/repos.json`, `evidence/<repo>.txt`, `batches/`). The register in this skill is the durable product; the scratch is its provenance.

## Refresh — keep the atlas true

- **After working in a repo** in any session where its role, canonical files, status, or watch-outs changed (or you learned they were wrong): update that repo's entry in `REGISTER.md` in the same session, then re-sync this skill to wbic16/emise-tools@exo (publish-tooling route) and rebuild the skills index (`~/workspace/phext/build_skills_phext.py`, then `--check` must print CURRENT). A stale entry is a defect of the same class as a stale register entry anywhere else.
- **Full re-audit** when the repo count has moved materially or Will asks: re-run the method above from the live list, diff entries against the previous register, and report the delta (new repos, tier changes, newly determinable unknowns). Do not silently overwrite — the diff is the report.
- **Unknowns are a work list.** The 16 unknown-tier repos from the first audit (brain-trolley, CoreThought, Cosmic-Cognitive, every-ast, exo-motes, gemini-connector, machine-elf, multi-chat, mytheon-arena, phext-demos, phext-ircd, phext-mail, phext-wiki, robospeak, sq-cloud, sq-howto) are mostly zero-size seeds or stubs whose names/descriptions are all that exist. When one gains content, its entry gets a real audit at that point.

## Boundaries — what this skill is not

- **Not coverage.** Whether every tool we depend on has a repo and a Jenkins job is the repo-coverage-census skill's question (Saturday pass). This atlas assumes the repos exist and says what they are for.
- **Not branch hygiene.** Branches without PRs, stale branches, and merged-history cleanup belong to the lost-work-sweep skill. Untouched-in-a-year pruning candidates belong to repo-pruning-check.
- **Not a sitemap.** The atlas carries no deploy or hosting state; it records importance, not location.
- The atlas never authorizes action in a repo. It informs the session that then works under the normal rules (every PR to Will carries its full URL; merges and publishes follow their own standing rules).

## First audit — 2026-11-20

226 repos audited from the live API list. Tiers: **flagship 13** (agi, emise-tools, exo-plan, human, libphext-rs, phccbox, phext-lattice, phext-shell, quarterexo, register, rfcbox, singular, SQ), **working 101**, **archive 96**, **unknown 16**. Statuses: active 87, quiet 123, seed-empty 16. 127 watch-out lines across the register; 29 repos carry GitHub Actions workflows and are flagged with the no-Actions rule (most inherited from upstream forks; phext-vr's was removed 2026-11-19/20 and its entry records that it now deploys via ranch Jenkins).
