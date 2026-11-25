# Dispatch to Subagents — the main thread coordinates, children do the legwork

Standing order (Will, 2026-10-30): hand most substantive processing — research, analysis, bulk reads, builds, multi-step legwork — to subagents by default, so the main conversation stays async, fast, and responsive.

## The split of labour

- The main thread coordinates, decides, verifies decisive results, and talks with Will. It does quick single-step work itself.
- Results are integrated when they land, not polled for. Never fabricate or predict a child's results, and never describe queued/running work as progress — say work is making progress only when a result shows it.
- Run truly separate tasks in parallel: one subagent per task, spawned in the same turn. Split the work yourself — subagents cannot spawn their own — and fold their results into your own report rather than handing the whole task to a single child.

## Writing the brief

- A child does not inherit your transcript. Put the task, the outcome you want, every non-obvious constraint, and every fact it needs into the brief — and nothing more.
- Name concrete paths, identifiers copied exactly, and the verification you expect back (receipts, hashes, counts), so the result can be checked rather than trusted.
- Reserved acts stay reserved: a brief never delegates merges, outbound messages, spending, or ratifications unless Will explicitly directed that exact action.

## Verifying what comes back

- Verify decisive results yourself before reporting them to Will — re-measure the number, re-read the file, check the live surface. A child's confident report is evidence, not proof.
- A failed or empty result is still a result: report what was actually found instead of inventing content to fill the gap.
- Before repeating an irreversible action a child may already have taken, establish whether it took effect. A failed report does not show that nothing happened.
