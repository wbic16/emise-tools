# Verify Quantified Results Before Sharing

## Scope the claim

- Write down the exact claim before verifying it, including the number, the artifact it came from and where the claim would be used.

- Treat any number supplied by a builder run, a subagent report or an earlier draft as unverified until you reproduce it yourself.

- Hold external use while verification is open, and say plainly that the claim is on hold rather than repeating it with a caveat.

## Reproduce from primary artifacts

- Reproduce the result from the primary artifacts, such as the actual store file, the live page or the remote tree, and not from a summary of them.

- Check that each input artifact is the intended one by recording its size and its SHA-256 hash before measuring it.

- Reject a measurement taken from an empty file, a zero byte store, a stale copy or a default project, and record why it was rejected.

- Check file modes as well as content hashes when the result involves published files, because a hash match does not show a lost execute bit.

## Run negative and mutation controls

- Run a no-change control and confirm the method reports no change on an unchanged copy.

- Run a mutation control by making one known change through a separate route and confirm the method names that exact change and nothing else.

- Run a scale control when the claim depends on size, because a method that works on a small input can fail or hang on a large one.

- Investigate a failed control as a defect in the method or the setup, and do not average it away or rerun until it passes without a recorded cause.

## Report the verdict

- Report the reproduced number with the controls that were run, the artifact hashes you measured and any control that failed.

- Withdraw or correct a claim already shared when reproduction contradicts it, and name the corrected number in the same channel.

- Release a held pitch, post or pull request only after the reproduction and the controls agree with the claim.

## Available connectors

- [GitHub](/opt/hatch/connectors/github/CONNECTOR.md) for reading remote repository state, files and pull requests when a claim concerns published code.

- [Github](~/workspace/custom-connectors/custom.github/CONNECTOR.md) for comparing a local file blob hash against the remote blob hash on the API publish route.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Shrink the claim to what you reproduced when the full headline number cannot be reproduced, rather than sharing the larger number with a warning.

- Ask the user whether to share a partial result when verification will take longer than the external deadline allows.
