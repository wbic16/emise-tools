# Phext Reference Conformance

## Use the reference implementation

- Use the existing reference implementation for the language in use, such as libphext-rs for Rust or the maintained binding for another language, whenever a tool parses, writes or serializes phext.

- Treat a request to build a phext parser or serializer by hand as a question to resolve before coding when a reference implementation exists, and name the reference you found or the search that found none.

- Derive every delimiter value, dimension order and coordinate rule from the reference implementation or its specification, and never reconstruct them from memory, from a neighbouring format or from the behaviour of your own earlier code.

- Record the reference name and version in the work record for the change, so a later reader can check which definition the code was built against.

## Test against files you did not write

- Build the conformance corpus from files produced by another implementation, another tool in the same ecosystem or the reference implementation itself, and never judge conformance only on files the code under test wrote.

- Round trip each corpus file through parse and serialize, then compare scroll contents and coordinates against the reference implementation reading the same file.

- Include the shapes that expose a self consistent wrong parser, such as a scroll edited by an external editor, an empty line inside a configuration shaped scroll, empty scrolls, and files at several delimiter depths.

- Add a regression test for every divergence you find, using the exact foreign file shape that exposed it, and keep that test in the suite after the fix lands.

- Treat a test suite that passes only on self written files as no conformance evidence, and say so plainly when that is all a run has shown.

## Contain a divergent implementation

- Stop extending a parser or serializer once a conformance run shows it disagrees with the reference on the same file, and replace it with the reference implementation instead of patching the divergence case by case.

- Treat state already written by a divergent serializer as suspect, because its files can look valid to the code that wrote them while other tools read them differently.

- Name the suspect state, where it lives and what a safe rebuild, wipe or reimport from a reference written source would take, and get the user direction the standing rules require before destroying it.

- Verify the replacement by rerunning the full foreign corpus after the swap, not only the case that failed first.

## Available connectors

- [Github](~/workspace/custom-connectors/custom.github/CONNECTOR.md) for reading the reference implementation and its published versions from the repositories that hold them.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Drive the reference implementation as a subprocess or through SQ for a one off read when porting it into the project would cost more than the task is worth.

- Ask the user before writing a new parser when no reference exists for the language in use, because a new implementation is a design decision rather than a coding detail.
