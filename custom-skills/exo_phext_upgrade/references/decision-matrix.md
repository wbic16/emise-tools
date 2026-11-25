# Phext upgrade decision matrix

Distilled from phext's definition, not from analogy. Phext is an interoperable
encoding layer: characters at 9D addresses (Library.Shelf.Series /
Collection.Volume.Book / Chapter.Section.Scroll), each scroll normal 2D text,
delimiters are ASCII control bytes (themselves valid UTF-8), coordinates are
1-based, internal to one phext, and most of the space stays empty as room to
grow. Delimiter bytes, highest to lowest: 0x01, 0x1F, 0x1E, 0x1D, 0x1C, 0x1A,
0x19, 0x18, 0x17.

## The five classification tests

Apply to each persistent or structured part of the project. A part is a strong
Class A (canonical phext) candidate when the yes answers cluster; a single
hard no from tests 4 or 5 can demote it to B, C or D.

1. **Text test** — Is the content text, or losslessly text-encodable without
   changing its meaning (integer sequences as decimal, small binaries as
   base64)? Weights/tensors fail: their meaning is their exact numeric bit
   pattern at scale, text encoding multiplies size and buys no addressability
   anyone will use.
2. **Identity test** — Do records have stable identity that survives edits
   (a slot, id, path, key)? Phext addresses are stable places; data whose
   identity is "row N in a file that gets rewritten" must gain a stable key
   first, or stay a bridge.
3. **Granularity test** — Do updates touch one record or field at a time?
   Per-field scrolls pay off exactly when mutations are local. Whole-blob
   rewrites on every change gain little beyond readability (still possibly B).
4. **Access test** — Would a reader ever want one record, one segment or one
   field without scanning the whole store? If the only access pattern is
   "load everything, in order, always", phext's win is diffability and
   provenance, not paging — say so honestly.
5. **Provenance test** — Does knowing who/what/when per record, or reviewing
   changes as text diffs, matter to this project? Phext in git, or hosted in
   SQ, makes every scroll individually selectable and auditable.

## Class summary

| Class | Meaning | Examples |
|---|---|---|
| A canonical | Phext is the store of record; native tools read/write scrolls | qwenFS disk image (segments per file), ranch admin records, journals, mailboxes |
| B derived view | Canonical data stays put; a phext materialization is rebuilt from it | Search indexes, catalogs, eval corpora generated from runs, docs assembled from code |
| C bridge only | Import/export both ways, verified byte-exact on the native side | Formats with external users, fixtures other tools consume, legacy migrations |
| D leave alone | No phext representation | Model weights and tensors, crypto material and secrets, hot-loop buffers, media binaries (embed as base64 only when a one-file corpus is the explicit goal, and note the xz-seal repayment) |

## Coordinate archetypes

Derive axes from the project's own invariants. Four recurring shapes:

- **Record store** — Book = stable record slot, Chapter = record part or
  revision, Section = field lane, Scroll = field value or value chunk.
  (Bickford Llama Ranch admin pattern: one SQ update per field edit.)
- **Segmented sequence** — Book = sequence/file, Chapter = segment in order,
  Section = lane (content, metadata, ack), Scroll = chunk within a segment.
  Version/base counters live in metadata scrolls so invalidation logic can
  key on them exactly as the native format did. (qwenFS pattern.)
- **Graph** — Volume = graph, Book = source node slot, Chapter = target node
  slot, presence scroll = edge. Unlink deletes one scroll. Derived reverse
  index (backlinks) is Class B, rebuilt, never stored twice as truth.
- **Corpus / library** — Volume = work or run, Book = part, Chapter =
  chapter, Section/Scroll = passage. Manifest at 1.1.1/1.1.1/1.1.1, table of
  contents as a scroll, provenance (source, hash, date) per volume.
- **Single-phext filesystem with WAL bookends** — when the project is itself
  a store or filesystem, give the whole coordinate space to one phext and let
  the caller (often an LLM) read and write scrolls directly, with no per
  record files beside it. Reserve an immutable start volume (manifest and
  genesis, written once at format) and an immutable end volume (checkpoint
  and a seal hash over all preceding bytes), put the data in a middle volume,
  and put an append-only hash-chained write-ahead log in its own volume:
  every mutation lands in the WAL first, then applies to the store, and open
  replays or truncates a torn WAL tail and verifies both bookends. Callers
  never write the start, WAL or seal volumes directly. (qwenFS variant
  pattern.)

## Encoding rules

- Text stays text. Integer sequences: comma-separated decimal (legible,
  diffable). Floats: only when the project already treats them as text with
  a stated precision — otherwise the data is probably Class D.
- Binary that must ride inside a scroll: base64 text. Measured on a mixed
  corpus (2026-11-04, mutable.phext.io analysis): after an xz-6 seal the
  residual cost of base64 was +1.69% corpus-wide, about 95% repaid, because
  base64 carries 6 bits per byte and the compressor reclaims the expansion.
- Never write raw non-UTF-8 bytes into a phext. A conforming phext is valid
  UTF-8 as a whole byte stream.
- No JSON blob scrolls. If a scroll's content needs a parser to find the
  field you want, the fields wanted their own coordinates.

## Verification minimum

Roundtrip both directions, byte identity on the deterministic native side,
edge cases from the project's own limits (empty, max count, self reference,
rewrite/version advance), one mutation control (one record changes, exactly
its scrolls change), SHA-256 on shipped artifacts, execute bits checked as
tree modes not just hashes, and a delimiter-walk cross-parse with an
independent parser (~/workspace/phext/parse_phext.py) plus a strict UTF-8
decode of the whole file.
