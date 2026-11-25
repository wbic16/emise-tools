# Recover Failed Job Outputs

## Verify what actually landed

- Start the recovery pass as soon as a delegated or background job fails, times out, or ends without filing its expected report, before dispatching any replacement work.

- Read the original brief and its expected outputs first, then check each named artifact, commit, file and record first-hand at the place it was supposed to land.

- Separate the results into landed and verified, landed but unverified, and missing, and cite the path, hash or count that proves each landed item.

- Check your own recovery brief against the source records before acting, because a wrong count or coordinate in the brief will send the recovery looking in the wrong place.

## Close loose ends in the original scope

- Complete only the loose ends that were already in the original scope, such as filing the missing report, publishing a finished artifact that never landed, or adding a finished item to its queue.

- Name each gap you cannot close from the landed work, and state plainly what is still owed instead of smoothing it over.

- Leave referenced material that does not exist anywhere untouched, and record it as a gap for the owner of the brief rather than improvising a replacement for it.

- Validate any recovered artifact with the cheapest real check available, such as a test run, a read back or a count against the expected total, before calling it recovered.

## Report the recovery honestly

- Report what landed, what you completed, and what remains missing in one pass, with the evidence for each claim.

- Record the recovery in the same task record as the failed job, so the next reader sees the failure and the recovery together.

- Dispatch replacement work only for the named missing pieces, with the recovery findings in the new brief so the replacement does not redo verified work.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Prefer recovering a partial result over rerunning the whole job when most units verify, because a rerun can overwrite good artifacts and wastes the work that did land.

- Rerun from scratch only when nothing landed or the landed work fails validation, and say which of those two reasons applies.
