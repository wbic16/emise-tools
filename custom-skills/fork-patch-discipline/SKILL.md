# Fork Patch Discipline — a fork is upstream plus an auditable patch set

How Emise maintains Will's forks (established on wbic16/mutable-os for mutable.phext.io; Will, 2026-11-04 / 2026-11-05): adjustments and feature support stay as tweaks/patches easily applied to upstream — the fork's divergence must always be replayable, never a snowflake tree.

## The rules

- **Patches, not divergence.** Every change the fork carries is a tweak/patch that could be re-applied to a fresh upstream checkout. If a change can't be stated as a patch, it doesn't belong in the fork.
- **PATCHES.md is the complete per-file record** of the fork's divergence: every file that differs from upstream, and why. If it isn't in PATCHES.md, it isn't a fork change.
- **Rebase program:** when divergence grows, squash the fork's changes into a small number of commits (ideally one phext commit), rebase onto current upstream, and re-verify. Preserve the old main as a named branch (e.g. emise/pre-rebase-main) before any history replacement. When Will asks for a rebase, the result is force-pushed (--force-with-lease, never bare --force) as the default — Will's standing ruling 2026-11-06 — UNLESS the rewrite would impact anyone except us (other collaborators' work, open PRs it would strand, external consumers of the history); impact beyond us means stop at a branch push and report. Force pushes outside a Will-requested rebase still need his explicit direction for that specific case.
- **Cutovers are total when Will rules them so:** on Mutable (2026-11-05) he directed full-phext with NO silent backwards compatibility — no dual-mode, no silent fallback, no old I/O paths; legacy/disk forms are upgraded on encounter, protected only by a backup copy or an explicit prompt. Record the ruling in PATCHES.md and the goal record with its date.
- **State lives outside the checkout:** deployed data (e.g. Mutable Caverns) lives outside the repo tree (e.g. /source/mutable-os-data/), so rebasing or replacing the checkout never touches live data.
- **Verify before publishing:** run the fork's own suite after any rebase or patch application, check tree modes as well as blob SHAs on publish (see publish-tooling), and hand Will a merge that has passed verification — a change that fails its own verification is reported as failed, not shipped hopefully.
