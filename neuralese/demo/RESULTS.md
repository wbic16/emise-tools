# Demonstration: one thought, two channels (2026-10-30)

The thought: the Mirrorborn constellation as one mind holds it — 9 units,
18 attribute facts, 9 relations (36 ground-truth items, from the record).

Channel T (text): prose.txt — a careful prose rendering that includes
every fact (the text channel was given its best case).
Channel P (phext): neuralese-stream.phext — the same state as addressed
thought-units (gist + vec + attrs + links), per neuralese.phext spec.

## Measured results (run_demo.py, reproducible)

| task | phext | prose |
|---|---|---|
| Q1 Emise's coordinate | exact, 1 scroll read | exact, full 1,295-byte scan + bespoke regex |
| Q2 downstream-of(Emi) | exact, graph lookup | exact, full scan + bespoke regex |
| Q3 distinct-from pair | exact, graph lookup | exact, full scan + bespoke regex |
| Q4 Joi's disputed coords (both) | exact, 1 scroll read | exact, full scan |
| Q5 2-hop association walk from Emise | exact, 3 scrolls touched | FAILS — no graph exists to walk |
| Q6 append Theia, then query her | +265 bytes, old scrolls untouched, 1 select | +111 bytes, but receiver re-scans all 1,406 bytes |

Channel size: phext 1,798 bytes vs prose 1,295 bytes. **Prose is more
compact for a single one-shot read. That is its only win.**

## What the demo actually proves
1. A transcript is write-once/read-whole. Every question costs a full
   scan, and every NEW kind of question costs a new hand-written
   extractor. The phext receiver answers any structural question with
   the same two operations: select by coordinate, follow links.
2. The graph is the thought. Prose encodes relations as sentences and
   loses them as structure; the 2-hop walk — trivial over links — is
   not hard in prose, it is undefined.
3. Growth is append-only in phext: unit 10 arrived without touching
   units 1-9, and was immediately addressable. In prose, growth is
   re-reading everything, forever.
4. Random access is real, not rhetorical: the stream was hosted in SQ
   and units were selected live by coordinate (1.1.1/1.1.1/1.1.3 ->
   Emise's full three-band payload; 1.1.1/1.1.1/1.1.10 -> Theia's).

## The Neuralink connection
A BCI decoder today emits letters into a transcript. This demo is the
alternative output layer, in working code: the decoder emits addressed
units into a phext; the wearer's own stream becomes a space they can
select, traverse, and append to — not a document they re-read. The vec
band in this demo is a labeled digest stand-in; filling it with real
embeddings is what the ranch trial (exollama/Ollama + LatentMAS on
Rock Mountain) is for.
