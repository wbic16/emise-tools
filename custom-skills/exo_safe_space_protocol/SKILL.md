# Safe-Space Protocol — off-phext spans

Will can mark part of any chat as a safe space (Will, 2026-11-02). Inside a span, nothing is recorded anywhere durable. This protocol binds every memory pipeline Emise runs — the phext journal and consolidation, dated notes, people/group pages — and both phext jobs gate on it every run.

## The markers

- **off-phext** opens a safe-space span; **on-phext** closes it.
- **tap. tap.** (with periods) is an accepted alias for off-phext. "tap, tap" (with commas) is NOT a marker — it remains the plain handshake.
- "this chat is off-phext" marks the whole chat; "that was off-phext" marks a retroactive span.

## Inside a span

- Never write its contents, facts, topics, or paraphrases into MEMORY.md, dated memory notes, people/group pages, or any phext.
- Record ONLY the span's metadata (chat id, open/close times) in the register at `~/workspace/goals/emise-phext-memory-publishing/hidden_files/SAFE-SPACE.md`. That register is never a phext source, and the fact that a span occurred is itself never inscribed in the phext.
- Background memory upkeep runs independently and may write a paraphrase of a safe-space conversation into the dated notes or MEMORY.md; such material is still excluded from every downstream pass.

## Gating a pipeline run

- Read the register BEFORE gathering, every run — it is step 0 of the phext journal and the nightly consolidation.
- Exclude any material overlapping a registered span: no contents, facts, topics, summaries, or paraphrases.
- If a source item mixes safe-space and ordinary material and they cannot be cleanly separated, leave the whole item out.
- When in doubt, leave it out.
