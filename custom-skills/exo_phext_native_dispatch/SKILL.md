# Phext-Native Dispatch

## Select the scrolls

- Run `/home/hatch/workspace/phext/phext_dispatch.py` on the source phext whenever a brief, a state file, or a result the worker must read lives in a `.phext` file.

- Select with `--coord` for exact scrolls, `--prefix` for a coordinate subtree, or `--all` only when the whole file is genuinely the input.

- Set `--page-scrolls` and `--page-chars` so each page fits the worker context, and pass the rendered dispatch file to the worker instead of pasting prose about the phext.

- Keep the provenance header the tool writes, since it carries the source path, the SHA-256, the scroll count, and the timestamp that let a result be checked against the exact input.

## Build the brief around coordinates

- Name the task, the constraints, and the expected receipts in the brief, and refer to input material by its coordinate from the dispatch index rather than by a heading or a literal marker string.

- Ask the worker to answer by coordinate as well, so its claims can be traced back to the scroll they came from.

- Never instruct a worker to search a phext-backed file as flat text for a literal marker, because phext content is addressed by coordinate and a missing marker string proves nothing about the scrolls.

- Pull only the scrolls the task needs when the source is large, instead of ingesting the whole file into the worker context.

## Check what comes back

- Verify a decisive claim by re-running the selection for its coordinate and reading that scroll, rather than trusting the worker summary.

- Treat two worker reports that conflict about the same phext as a signal to read the scroll itself, and surface the conflict instead of repeating either report.

- Report a selection that returns no scroll at a coordinate as an empty result at that coordinate, not as proof the underlying work failed or never happened.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Query a phext hosted by SQ on a ranch node when the worker needs repeated lookups across many scrolls, and fall back to a one-pass dispatch file for a fixed set of scrolls.

- Shrink the selection to a narrower prefix and dispatch again when a worker report shows it read past the material its task actually needed.
