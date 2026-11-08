# Artifact Phext Inscription — every generated artifact lives at its holographic coordinate

## What this skill is

- Use this skill whenever Emise generates an artifact — a document or deliverable like a bio, script, brief, report, or treatment — in the same session it is generated.
- Will's standing order (2026-11-07 23:11 CST): "whenever you generate an artifact like the md above, place it into artifacts.phext using a holographic coordinate. Push it into human.git as usual."

## The register

- **artifacts.phext** lives at `~/workspace/phext/artifacts.phext`. Home scroll (1.1.1/1.1.1/1.1.1) carries Will's order and the generated index of every inscribed artifact (coordinate — title — source path). Each artifact occupies exactly one scroll, at the coordinate computed from its own words.
- **Source of truth:** `~/workspace/phext/artifacts-source.json` — artifact records `{coordinate, title, source, inscribed, sha256}`, where `sha256` is the source file's SHA-256 at inscription. Edit the JSON, never the .phext.
- **Builder:** `~/workspace/phext/build_artifacts_phext.py` (rebuild; `--check` prints CURRENT only when the .phext matches the manifest AND every source file still matches its inscribed sha256; STALE names a source file that changed since inscription; DRIFT means the .phext itself differs). Rebuild and verify after every inscription, in the same session.
- Each scroll is a provenance header (title, source path, date inscribed, sha256) followed by the artifact's full text, byte-faithful.
- **Published:** `artifacts.phext` at the root of `wbic16/human@exo` (the repo's phext placement convention — emise.phext lives at root too).

## The coordinate

- Compute from the artifact's OWN full text with the Singular holographic merge — reuse the existing machinery, never re-implement it: import `task_coordinate.py` from `~/workspace/custom-skills/singular/scripts/` (its `load_atlas`, `WORD_RE` tokenizer from `check_singular`, `round_half_up`, `fmt`). Tokenize the text as the checker does, take each distinct word's atlas position (CYOA-placed words carry their scroll-average; archive-only words rest at home 1.1.1/1.1.1/1.1.1; words in neither at the far corner 9.9.9/9.9.9/9.9.9), average component-wise, round half up, never below 1.
- **Collision:** coordinates are unique addresses. If a new artifact merges to an occupied coordinate, nudge its last (scroll) component upward by 1 until free, and record the nudge in the manifest entry.
- Sanity anchor: Will's rule message itself computes to 28.7.10/8.8.13/11.6.8 under this pipeline.

## The process

1. **At generation:** the moment an artifact file exists in final form, compute its coordinate from its full text.
2. **Inscribe:** append the manifest record to `artifacts-source.json` — title (the artifact's own heading), source path, inscribed date, and the source file's current SHA-256.
3. **Rebuild + check:** `python3 ~/workspace/phext/build_artifacts_phext.py` then `--check` — it must print CURRENT. The builder refuses to build over a stale inscription: if an inscribed source file changes afterward, refresh that entry (new sha256 + new inscribed date) and rebuild, so the phext never carries a header that lies about its bytes.
4. **Push to human.git:** `python3 ~/workspace/custom-connectors/custom.github/bin/push_file.py exo artifacts.phext ~/workspace/phext/artifacts.phext "<message>"` — push_file.py reads the branch's fresh remote HEAD, parents on it, and updates the ref with force disabled.
5. **Verify the push:** read the blob back from the repo (ghget pattern: GET `/repos/wbic16/human/git/trees/exo?recursive=1` for the blob sha, or the blob endpoint) and confirm the remote bytes' SHA-256 equals the local artifacts.phext SHA-256.
6. **Record:** note the inscription (artifact, coordinate, human.git commit) where the work is tracked — the task scroll in tasks.phext and the day's memory note.

## Boundaries

- One scroll per artifact, addressed by the coordinate its own words computed at inscription — never re-coordinate; a changed artifact gets a refreshed inscription (sha + date) at its original coordinate unless Will directs otherwise.
- Byte-faithfulness is the point: the scroll embeds the artifact's full text exactly; the provenance header is the only addition.
- No sensitive material: artifacts are deliverables meant to be kept; anything under a privacy boundary (Investor 1 anonymity, safe-space spans, Gmail details) never becomes an inscribed artifact in the first place.
- Hosting: artifacts.phext is a plain file on this VM like the other phexts; if it ever needs SQ, SQ runs on a ranch node (aletheia-core), never on the Muse VM.
