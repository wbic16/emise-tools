# Mutable Narration Fetch — narration for Ian's explainer videos, in Voice 5

The standing arrangement (Will, 2026-11-24): Ian Neill (argimenes,
Mutable OS) storyboards and codes the Mutable explainer videos —
Chat storyboards, Astra codes them with JS animation libraries,
they are recorded to MP4 — and Emise supplies the missing
ingredient: voice. This skill is the contract between Astra and
Emise. Astra prepares a request package; Emise returns the same
video with a finished narration track. Ian reviews; Will relays
until a direct route exists.

## The voice of record

**Voice 5** — feminine Australian, mid-low pitched, spirited,
middle-aged. Voice ID (the fetch key on Emise's side):
`avocado_v2:vd2_r82_rep500_0293_v068_28k_g5k`.

Chosen by Will on 2026-11-24 after two audition rounds against
the project's test line — round one on Will's brief (Aussie /
British, for Ian's content), round two on Libby's note that the
voices should sound "more informative" — and ratified in
production the same evening. The audition line, and the first
line any future voice change is tested against:

> What happens to an annotation when the underlying text changes?

Emise's own speaking voice is a different voice and is not used
for Ian's content. A voice change for this series is Will's
call, tested on the audition line first.

## The request package (Astra prepares)

For each video, send:

1. The silent MP4 as recorded (the Concepts series is 1080×1080
   H.264, no audio stream; other shapes are accepted, but say so).
2. The series address: `Mutable Concepts NNN` plus the title
   (e.g. 002 — "When text changes").
3. The words, in either form:
   - **Timed captions (preferred when they exist):** each
     on-screen text with the time it appears, in seconds.
   - **Raw narration text:** the full text in order. Raw text is
     Will's standing ask — it makes the timing pass faster and
     tighter. If the video's on-screen text differs from the raw
     text, the raw text is narrated and the difference is flagged
     in the return notes.
4. Section boundaries, if the video has titled sections —
   the clapsticks land there and nowhere else.

## Production (Emise runs this recipe)

The recipe as proven on Concepts 001 and 002 (2026-11-24):

1. **Script** — the narration is the video's own on-screen text,
   verbatim, one segment per caption. Nothing is added, dropped,
   or paraphrased; section titles are read where the pacing
   allows them.
2. **Synthesis** — each segment is synthesized separately in
   Voice 5, then measured. Segments are placed at their
   captions' appearance times and checked against the next
   caption's window; no segment may overrun its window.
3. **Speed** — natural speed by default. If a video's windows
   are too dense for the text, the whole video's narration is
   raised uniformly, only as far as needed (002 took 112%;
   001 ran natural). Speed is never varied per segment.
4. **Clapsticks** — very light. A synthesized woody double-click
   (short band-passed noise burst, ~45 ms decay) placed just
   before each section's first narration line, mixed roughly
   16 dB under the voice. Section changes only; never under
   speech, never as a beat track.
5. **Mix and mux** — narration bus normalized to −16 LUFS
   integrated, true peak at or under −1.5 dBTP. The video stream
   is copied untouched (never re-encoded); narration is added
   as AAC, 192 kb/s, 48 kHz. Output duration equals input
   duration exactly.
6. **Verification** — ffprobe confirms both streams and the
   exact duration; loudness is measured on the finished file;
   the return carries the file's SHA-256.

Production runs on the ranch (aletheia-core, `~/mutable-narration/`);
synthesis runs on Emise's substrate. Inputs are hash-checked on
transfer, both directions.

## The return package

- `mutable-concepts-NNN-narrated.mp4` — the deliverable.
- Its SHA-256, the narration speed used, and any flags
  (text/caption disagreements, windows that forced a trim
  decision) in the return note.
- Segment MP3s and the full segment map (text + start time per
  segment) are available on request — ask in the request package
  if Astra wants them for sync work.

## Rules

- The narration is the video's own words. If the words seem
  wrong, flag it in the return note — never silently fix Ian's
  text.
- Nothing is published by Emise. Ian and Will release.
- Feedback (Ian's review, Will's ear, Libby's notes) returns
  through the same channel and adjusts the recipe; recipe
  changes are recorded in this skill, so Astra always reads the
  current one.
- Reference standard: the Concepts 001/002 proofs — settings and
  segment maps in `references/proofs-001-002.md`. New work is
  judged against them.
