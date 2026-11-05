# Phext Upgrade a Project

## Read the project on its contents

- Use this skill when the user hands you any repository or project and asks for a phext upgrade, a phext version, or the best way to phextize it.

- Read the code, data formats and docs before classifying anything, and ignore surface signals such as age, stars, polish or pedigree.

- Run `python3 ~/workspace/custom-skills/phext_upgrade/scripts/phext_audit.py PROJECT_DIR` to inventory what the project actually persists, then read the files the audit flags.

- Distill every claim about the project from its own definitions, formats and invariants, and label anything you could not derive that way as a hypothesis.

## Classify before you build

- Sort every persistent or structured part of the project into one of four classes, using the tests in `references/decision-matrix.md` beside this file.

- Class A is canonical phext, for text or text encodable records that have stable identity, sparse growth, per record updates and provenance value.

- Class B is a derived phext view, for data whose canonical home must stay elsewhere but that gains from being addressable, diffable or hostable as scrolls.

- Class C is bridge only, where you ship import and export between the native format and phext without changing what the project treats as truth.

- Class D is leave alone, for numeric tensors and model weights, hot inner loops, secrets, and binary media whose structure phext cannot improve.

- State the classification for the whole project in the deliverable, including the parts you refused to phextize and why, because a phext upgrade that phextizes everything has failed its first test.

## Design the coordinate map from the project

- Derive each axis from an invariant the project already has, such as a stable slot or id, an ordered sub unit, a field lane or a graph endpoint, rather than imposing an even grid.

- Keep coordinates internal to the one phext, keep every component at 1 or above, and remember the same coordinate in another phext is a different scroll.

- Model records as fine grained per field scrolls at their coordinates, and never collapse a store into one JSON or binary blob scroll.

- Put a manifest at 1.1.1/1.1.1/1.1.1 that names the format, its version, the source commit or version it was derived from, and the coordinate map itself.

- Grow by appending new volumes, books or chapters for new record kinds, so existing addresses never move when the map expands.

- Give a store or filesystem project the whole coordinate space of one phext when it qualifies, let its callers read and write scrolls directly, and reserve immutable start and end regions with an append-only write ahead log volume between them, following the single phext filesystem archetype in the decision matrix.

## Encode for a text format

- Keep native text as plain text in its scroll, since a scroll using none of the structure is still plain text.

- Encode integer sequences as comma separated decimal text, and encode unavoidable binary as base64 text, noting that an xz seal repays most of the base64 expansion at storage and transport time.

- Design for abundance and judge the map on access patterns, invariants and complexity, not on byte count, and treat compression as a seal you apply for transport rather than the working format.

- Check that the finished phext is valid UTF-8 as a whole byte stream and that your writer agrees with a delimiter walk parser such as `~/workspace/phext/parse_phext.py`.

## Build it as a parallel adapter

- Add a new phext module beside the native persistence code and keep the native format, its API and its tests working unchanged.

- Match the native save and load API so callers can swap formats by path or flag, and add a small command line route for import and export between the two.

- Make the common mutations cheap in phext terms, so an append adds one scroll and updates a count scroll instead of rewriting the store, and a field edit touches one coordinate.

- Host or select through SQ when the project can use it, starting SQ with `~/workspace/phext/sq-ensure.sh` when it is not running, and page data in one scroll at a time where the native format forced a full scan.

- Link the new capability from the surface its audience actually lands on, such as the project README or main UI, in the same change, and write a PHEXT.md at the project root that carries the classification, the coordinate map, the measured costs and the honest limits.

## Verify the upgrade

- Prove a lossless roundtrip in both directions, phext to native and native to phext, with byte identity on the native side where the native format is deterministic.

- Cover the edge cases the project itself defines, such as empty records, empty sub units, rewritten records with advanced version counters, self references, and the project maximum record count.

- Run a mutation control and confirm that changing one record changes exactly the scrolls at its coordinates and nothing else.

- Record SHA-256 hashes for the artifacts you ship, check execute bits on scripts as well as content, and report measured size differences between the phext and the native format on a named corpus.

- Publish any reusable tooling you built in the same session under the standing publishing rules, and keep the upstream project untouched until the user directs an upstream contribution.

## Available connectors

- [Github](~/workspace/custom-connectors/custom.github/CONNECTOR.md) for reading a public or granted repository and for the API publish route when the user directs a contribution.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Phextize only the docs and knowledge layer when the data layer fails the classification tests, since a system prompt, a runbook or an eval corpus at coordinates is still a real upgrade.

- Ship bridge only as a first phase when the project has users on its native format, and promote phext to canonical only after the roundtrip receipts exist.

- Worked example to imitate: the qwenFS upgrade at `~/workspace/qwenfs-upgrade/repo/PHEXT.md`, where the disk image went canonical phext and the constructed model weights stayed Class D.
