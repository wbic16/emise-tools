# CYOA Traversal Map

Built by Emise, 2026-10-30, at William's direction: "build a coordinate traversal map
that mirrors how I traced my mind in CYOA. once you have 1,000 scrolls placed, switch
to 2-digit coordinates. see mytheon in the material."

## What the map is
CYOA (choose-your-own-adventure.phext) read as a traversal, the way the Mytheon Arena
scrolls describe play: no fixed path; scrolls offer jumps; you follow what speaks.
Two edge systems over the same 829 placed scrolls:
- TRACE edges (828): consecutive scrolls in file order — the order the mind moved
  while writing, recovered by the dead-reckoning parser (~/workspace/phext/parse_phext.py).
- LINK edges (537): coordinates named inside a scroll's text that resolve to placed
  scrolls — the jumps the scrolls themselves offer.
Plus one whitespace-only ghost scroll at 8.1.1/1.1.1/1.1.1 (no content; SQ counts it,
which is why SQ says 830 and the parser says 829 content scrolls).

## Traversal coordinates and the 1,000 rule (Emise's implementation of William's spec)
Each placed scroll also receives a TRAVERSAL coordinate: its position in the trace,
counted on a base-9 odometer across the nine phext slots (components 1-9, last slot
fastest), starting at 1.1.1/1.1.1/1.1.1 — which the first scroll therefore holds in
both address systems at once. While fewer than 1,000 scrolls are placed, components
render as single digits (Epoch 1). At 1,000 placed, components render zero-padded
2-digit (Epoch 2, e.g. 01.01.01/01.01.01/01.01.01). CYOA places 829, so the map is
Epoch 1 throughout. The rule lives in one function (tcoord) in the generator, so a
different reading of William's sentence can be swapped in without touching the data.

## Files
- cyoa-traversal.json — nodes (index, original coordinate, traversal coordinate,
  title, chars), link edges (by node index), epoch, ghost, and the rule as data.
- index.html — self-contained interactive map: golden-angle spiral layout in trace
  order, walk-the-trace playback, layer toggles, search by title/coordinate,
  click any node for both its addresses.

## Hubs (most inbound links)
1.1.1/1.1.1/1.1.1 (26) · 1.1.1/1.1.1/1.1.2 Emi (13) · 1.1.1/1.1.1/1.1.3 (9) ·
2.1.1/1.1.1/1.1.1 Mytheon (7) · 1.2.3/4.5.6/7.8.9 Kai (6)
