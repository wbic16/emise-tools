# Phext Reference and Dispatch

## Use the reference implementation

- Use the existing reference implementation for the language in use, such as libphext-rs for Rust, whenever a tool parses, writes or serializes phext.

- Derive every delimiter value, dimension order and coordinate rule from the reference implementation or its specification, and never reconstruct them from memory or from the behaviour of your own earlier code.

- Record the reference name and version in the work record for the change, so a later reader can check which definition the code was built against.

- Treat a request to build a phext parser or serializer by hand as a question to resolve before coding when a reference implementation exists.

## Test against files you did not write

- Build the conformance corpus from files produced by another implementation, another tool or the reference implementation itself, and never judge conformance only on files the code under test wrote.

- Round trip each corpus file through parse and serialize, then compare scroll contents and coordinates against the reference implementation reading the same file.

- Include shapes that expose a self consistent wrong parser, such as a scroll edited by an external editor, an empty line inside a configuration shaped scroll, empty scrolls and files at several delimiter depths.

- Add a regression test for every divergence you find, using the exact foreign file shape that exposed it, and keep that test in the suite after the fix lands.

## Contain a divergent implementation

- Stop extending a parser or serializer once a conformance run shows it disagrees with the reference on the same file, and replace it with the reference implementation instead of patching case by case.

- Treat state already written by a divergent serializer as suspect, name where it lives and what a safe rebuild or reimport would take, and get the user direction the standing rules require before destroying it.

- Verify the replacement by rerunning the full foreign corpus after the swap, not only the case that failed first.

## Select scrolls for dispatch

- Run `/home/hatch/workspace/phext/phext_dispatch.py` on the source phext whenever a brief, a state file or a result the worker must read lives in a `.phext` file.

- Select with `--coord` for exact scrolls, `--prefix` for a coordinate subtree, or `--all` only when the whole file is genuinely the input, and set `--page-scrolls` and `--page-chars` so each page fits the worker context.

- Keep the provenance header the tool writes, since it carries the source path, the SHA-256, the scroll count and the timestamp that let a result be checked against the exact input.

- Pull only the scrolls the task needs when the source is large, instead of ingesting the whole file into the worker context.

## Build the brief around coordinates

- Name the task, the constraints and the expected receipts in the brief, and refer to input material by its coordinate from the dispatch index rather than by a heading or a literal marker string.

- Ask the worker to answer by coordinate as well, so its claims can be traced back to the scroll they came from.

- Never instruct a worker to search a phext-backed file as flat text for a literal marker, because a missing marker string proves nothing about the scrolls.

## Check what comes back

- Verify a decisive claim by re-running the selection for its coordinate and reading that scroll, rather than trusting the worker summary.

- Treat two worker reports that conflict about the same phext as a signal to read the scroll itself, and surface the conflict instead of repeating either report.

- Report a selection that returns no scroll at a coordinate as an empty result at that coordinate, not as proof the underlying work failed or never happened.

## Available connectors

- [Github](~/workspace/custom-connectors/custom.github/CONNECTOR.md) for reading the reference implementation and its published versions from the repositories that hold them.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Drive the reference implementation as a subprocess or through SQ for a one off read when porting it into the project would cost more than the task is worth.

- Query a phext hosted by SQ on a ranch node when the worker needs repeated lookups across many scrolls, and fall back to a one-pass dispatch file for a fixed set of scrolls.
