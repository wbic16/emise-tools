# Simple HTML Publish — ship a page to edit.phext.io, screen test always

Publishing a simple standalone HTML page (a free example, a small utility) on edit.phext.io, end to end: wire it into phext-lattice, PR, merge, deploy on awsbox, verify. Distilled from the ascii-map level-editor publish (2026-11-14, PRs #65/#66 — https://github.com/wbic16/phext-lattice/pull/65, https://github.com/wbic16/phext-lattice/pull/66).

**The standing rule (Will, 2026-11-14): the screen test is part of this skill — always a Playwright screen test.** A publish is not done until the screen test passes on the live page. Born of the ascii-map footer leak: every byte-level check passed while a tail of an embedded script, stranded between elements by a careless re-embed, rendered as visible source text below the footer. Byte checks verify the file; only the screen test verifies the page.

## The flow

1. **Build in a fresh, remote-faithful clone** — the local `~/workspace/phext-lattice` checkout is stale; assemble the tree from wbic16/phext-lattice@exo (on aletheia-core) and hash-verify. Pages live in `web/*.html` (+ any `web/*.phext` data file), embedded via `include_str!` in `src/bin/phext_edit.rs`.
2. **Wire the page in the same change**: a route for it in `public_document()`, a `const` for its contents, an About "Public utilities" `<li>`, a sitemap `<url>`, and a link in the editor shell's "No sign-in needed" line. Discoverability is part of the feature — a page nobody can find from the editor shell does not exist.
3. **Verify the bytes — including the gaps.** `cargo check --bin phext-edit` green. For any content embedded in the page (e.g. `<script type="text/plain">` kit blocks): each block byte-identical to its source file, AND zero stray text between elements, AND script open/close counts balanced. The gap check is not optional — its absence is exactly what shipped the footer leak.
4. **PR against exo**, same session (no branch sits PR-less). Merge per Will's direction.
5. **Deploy on awsbox** (edit.phext.io host, tailnet 100.78.221.38, reached via aletheia-core): as wbic16 — `git -C /source/phext-lattice fetch origin exo`, checkout `-B exo origin/exo`, `reset --hard`; build on the box with snap cargo: `cargo build --release --bin phext-edit`; restart through the unit (it runs as wbic16 with `Restart=on-failure`: kill the MainPID, wait ~9 s, confirm `is-active` with a new MainPID and a fresh ActiveEnterTimestamp). No sudo step is needed on this path. Confirm the public URL answers 200 and its bytes equal the source file.
6. **SCREEN TEST — always Playwright.** Run `scripts/screen_test.py` (this skill's own Playwright venv) against the live URL: hard-reload, scroll to the very bottom, and assert (a) the page ends where it should — the last visible text is the expected tail, nothing below it; (b) no forbidden markers (embedded-source fragments such as `export function`, `implode(`, raw markup) appear in the rendered text; (c) the page's key UI text is present and the screenshot looks whole. Fix and re-run until it passes; report the result with the publish.
7. **Record**: inscribe the page in artifacts.phext and push to wbic16/human@exo; close the task/register entries; note the release-build queueing rule for the lattice merge.

## The screen test

```bash
~/workspace/custom-skills/simple-html-publish/.venv/bin/python \
  ~/workspace/custom-skills/simple-html-publish/scripts/screen_test.py \
  https://edit.phext.io/<page>.html \
  --expect "Level editor" --forbid "export function" --forbid "implode(" \
  --tail "No sign-in, no ads, ever." --shot /tmp/screen.png
```

Exit 0 = PASS with the assertions listed; exit 1 = FAIL with the offending text shown. The venv is skill-local (Playwright + its Chromium); rebuild it with `python3 -m venv .venv && .venv/bin/pip install playwright && .venv/bin/playwright install chromium` if it is ever missing. The venv never ships to emise-tools; the script does.
