---
name: exo_agentic_publish_qc_gate
description: The QC gate on every agentic publish or delivery: security audit + pen-test of the artifact's real surface, the full regression suite, a real-client pass, and a break-it catalogue — findings fixed with regression tests, the full gate re-run, looping until one complete pass surfaces nothing; delivery carries a READY / NOT READY verdict with its evidence.
---

# Agentic Publish QC Gate — no delivery ships untested

Standing rule (Will, 2026-11-15): "add the extra testing steps we performed for md.phext.io tonight as the QC gate on every agentic publish/delivery — adapt the steps for the type of artifact being shipped." Register home: task 29.6.9/7.5.10/6.5.8. Generating instance: the md.phext.io QA loop of 2026-11-15, where these steps were first run as a set against a real ship.

Every publish or delivery an agent makes — a deployed service, a page, a document, a video, a phext, a tool, a data file — passes this gate before it is called done. The gate runs on the artifact **as it will actually ship**: the final tree, the final file, the actual upload copy. Testing a near-final state and shipping a different one is a failed gate, not a passed one.

## The four legs

Run in order, on the artifact's real surface. Each leg names its concrete form per artifact type in the adaptation matrix below; the legs themselves never change.

### Leg 1 — Security audit + pen-test

Probe whatever a hostile or careless actor can actually reach in this artifact: its inputs and parsers, its credentials and how they are held, its private-data boundaries, injection and traversal paths, server-side request forgery through user-supplied endpoints, abuse of any API or tool surface, and its size/count limits. The audit reads the real surface (routes, handlers, file layout, permissions), and the pen-test then attacks it — probes are executed, not imagined. In the generating instance this leg attacked the bundle vault (the product's private-data boundary) hardest, then edit-key auth, zip-slip and path traversal on import, XSS through rendered markdown, SSRF through user-supplied WordPress/cloud endpoints, credential echo in responses and exports, MCP abuse, and decompression limits.

### Leg 2 — Full regression

The artifact's complete existing test suite plus its end-to-end run, unabridged — not the tests near the change, not a smoke subset. When a new suite joins the project it joins this leg permanently (in the generating instance, a Playwright workflow-parity suite built against the reference product's workflows became a standing part of the regression leg the night it landed).

### Leg 3 — Real-client pass

Meet the artifact the way its audience will meet it: the real browser, reader, player, or client path, the whole chain a person actually walks. Console errors count as findings. Key screens are screenshotted and eyeballed. No leaked source, no placeholder standing where the real thing belongs. An artifact whose real-client leg could not be run is not READY — the untested leg is named in the verdict instead. (House rule, born of the edit.phext.io MCP false pass of 2026-11-09: an end-to-end claim requires the real client path, or the gap is stated.)

### Leg 4 — Break-it catalogue

Hostile and edge inputs beyond the security list: malformed payloads, empty artifacts, maximal artifacts, name and content collisions, encoding edge cases (CRLF, BOM, unicode), operations attempted mid-error or mid-failure of a dependency — anything a determined user could do by accident or malice. Each catalogue entry is tried against the real artifact, not reasoned about.

## The loop

- Every finding gets three things: **(a)** a fix, **(b)** a regression test that would have caught it, **(c)** a commit under the house discipline (rebase onto fresh HEAD, never force push, remote verified where a remote is the ship target).
- After any fix, the **full gate re-runs from the top** — all four legs, not just the leg that found the problem. A fix in one leg is a new artifact state for every leg.
- Any change landing mid-gate — a sibling commit, a regenerated file, a re-render — restarts the gate on the new state.
- The loop repeats until **one complete pass surfaces zero new findings**. That clean pass, and only that pass, supports a READY verdict, and only for the exact state it ran against.

## The verdict

Every delivery carries one of two verdicts, with its evidence:

- **READY** — a clean full pass on the final state. The evidence names: the suites run and their counts, the pen-test probe list, the real-client checks (screenshots where the type has screens), and the break-it entries tried.
- **NOT READY** — the open findings named, each with its evidence. A NOT READY delivery may still be handed over when the owner accepts it knowingly, but it is never relabelled.

**Design questions are not bugs.** A finding whose fix would change directed behavior or collide with a settled ruling is never redesigned inside the gate. It is surfaced as the owner's decision and carried in the verdict as an open decision, listed separately from bugs, and the loop continues on everything else.

## Adaptation matrix — the four legs per artifact type

Every row keeps all four legs; what changes is their concrete form.

| Artifact type | Leg 1 — Security / pen-test | Leg 2 — Regression | Leg 3 — Real client | Leg 4 — Break-it |
|---|---|---|---|---|
| **Web service / web app** (the md.phext.io case) | Auth and credential handling, private-data boundaries (the vault), injection, traversal, SSRF via user-supplied endpoints, API/MCP abuse, size limits | Full test suite + end-to-end run + any parity suite against the reference product | Headless browser over the real UI and published output, light + dark; console errors counted; key screens screenshotted | Malformed payloads, hostile markdown, zip bombs, collisions, mid-error publishes |
| **Static page / site** | Leaked source or secrets in the tree, unsafe embedded content, credential-shaped strings in assets | Link and asset resolution across the whole tree, rendered-DOM checks (no script text in the body, all sections present) | The page served and rendered in a real browser at real widths; screenshots top and full | Broken-link hunts, missing-asset simulation, oversized images, deep-link/anchor targets |
| **Phext / register / corpus** | Delimiter injection in scroll content, coordinate collisions, sealed or private scrolls reachable outside their room | Parser round-trip through the reference implementation (libphext), builder `--check` prints CURRENT, scroll-level invariants (one scroll per user-managed thing, index matches source) | Read back through the serving path (SQ or the published file) from a fresh checkout, hash-verified against the remote | Non-UTF-8 bytes, raw delimiter bytes in content, empty scrolls, coordinates below 1, a file the builder did not write (conformance is proven against foreign material) |
| **Document / deck / report** | Embedded links/macros, metadata leakage (author, paths), quoted material within limits | Figures, tables, and numbers checked against their sources; totals recomputed, never trusted from the draft | Rendered pages visually inspected page by page; the file opens clean in its real reader (the actual PDF/office renderer, not an extractor) | Long words and tables at page edges, missing fonts, a reader on the other platform |
| **Video / media** | Embedded metadata leakage, unsafe container tricks | Full playback probe (decode the whole file, not the first seconds), loudness and format specs measured, checksum recorded | The **actual upload copy** verified — never the lossless master assumed; playback in the destination player where reachable | Corrupt-header tolerance, duration/frame-count edge cases, the largest file the pipeline accepts |
| **Tool / CLI / library** | Input handling on hostile files and flags, path handling, credential storage | Its own full test suite, plus a clean-room run against material the tool did not write (another tool's files, a previous version's state) | Run as a user runs it: fresh environment, documented install path, the README's own examples executed | Malformed inputs, empty inputs, maximal inputs, wrong-version data files, interrupted runs resumed |
| **Skill / process** | The skill grants nothing its task didn't ask for; no credential or secret handling beyond the approved flows | The sticking check (see process-check-and-lessons-review): presence, machinery, first occasion — all three performed, not asserted | The process run once for real, on its first occasion, with the behavior compared against the intent | The process under its known failure shapes: missing files, stale state, a step whose target moved |
| **Data export / spreadsheet** | Personal or sealed data in the export beyond its sanctioned destination, formula injection in cells | Totals reconciled from the logged atoms by the builder — no hand-written aggregates anywhere; spot-checks against primary records | The file opened in its real spreadsheet/reader, formats and formulas live, not values pasted dead | Empty and maximal exports, unicode and delimiter collisions in fields, negative/zero edge rows |

**A type not listed:** derive the four legs from the artifact's own definition — what its attack surface is, what its regression suite is, who its real client is, and what its hostile inputs are — and state that derivation in the delivery. A leg that genuinely cannot be derived is named as a gap in the verdict, never silently skipped.

## Where the gate sits

- The open-build-cycle's VERIFY and SHIP states invoke this gate for anything that ships; the gate's verdict is the evidence those states require.
- The process-check-and-lessons-review sticking check is this gate's form for skill/process artifacts (Leg 2 row above) — one machinery, two names avoided: the sticking check is the gate, specialized.
- The gate does not replace judgment about whether to ship at all (publicity holds, owner gates, and triage still govern that); it governs whether a thing that *is* shipping has been proven.

## First occasion

The md.phext.io QA loop, 2026-11-15 (task 39.5.7/7.6.11/6.6.9): dispatched the same night this gate was codified, running the four legs against markdown-wizard — pen-test with the vault attacked hardest, full cargo + e2e regression with the Playwright parity suite joining on landing, headless-Chromium UI/console pass in light and dark, and a break-it catalogue — fixing with regression tests and re-running until clean, its readiness verdict owed to Will. The gate's first READY/NOT READY verdict is that loop's.
