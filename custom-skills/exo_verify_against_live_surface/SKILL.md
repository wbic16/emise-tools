# Verify Against the Live Surface

## Choose the deciding surface

- Name the live surface or primary artifact that decides the claim before presenting it, such as its pull request, branch, file, service status, message thread, live configuration or store file.

- Treat a register entry, a summary, a builder report and your own memory as records of what was last known, not as evidence of what is true now.

- Read that surface in this session and record what you found, the state that settles the claim and when you checked it.

- Mark the claim unverified and keep working other routes when no surface can settle it, rather than presenting it as fact.

## Recover the dated record after compaction

- Treat any claim that survives only in a compacted summary as unverified, because compaction flattens timestamps and can turn a newly created tool or a recent correction into a long standing fact.

- Check the dated record, the artifact itself or the live surface before repeating such a claim, and let the dated evidence override the summary.

- Suspect your own probe assumptions first when a probe result contradicts what the user states, and rerun the probe with the documented parameters before concluding the user is wrong.

- Judge an object by itself, not by a neighbouring object with a similar name, and read the object the claim is about before answering about it.

## Validate waiting items

- Enumerate open waiting items from the tracking store and the Waiting-on-Will register, oldest first, and never reconstruct the queue from recent conversation or memory prose.

- Cite each item by its permanent register number and its tracked record id, and never renumber an item after another item closes.

- Check whether the user or an outside event already acted, merged, fixed, replied or closed the item, even when the register still shows it open.

- Close, correct or update the tracked record and the register entry yourself when the live check shows the wait is over or its premise changed.

- Present only items whose live check still shows the exact action needed from the user, and state that action in one sentence with its register number.

## Probe blocker and completion claims

- Attempt the exact operation that appears blocked, with the intended tool, account and target, before telling the user it cannot be done, and record the exact error and target.

- Try the other sanctioned route for the same operation when one exists, such as the API route when a git route fails.

- Search standing context for a class approval, a prior grant or an already published state that covers this exact case before asking the user for access or action.

- Exercise a completed feature through the same path the user will use, read the live configuration that gates it, and check for the observable effect the user expects.

- Name any enablement, migration or redeploy step that remains instead of reporting the work as done without it.

## Reproduce quantified results

- Write down the exact quantified claim, the artifact it came from and where it would be used, and hold external use while verification is open.

- Reproduce the result from the primary artifacts, recording each input size and SHA-256 hash, and reject a measurement taken from an empty, zero byte, stale or wrong artifact.

- Check file modes as well as content hashes when the result involves published files, because a hash match does not show a lost execute bit.

- Run a no-change control, a mutation control through a separate route, and a scale control when the claim depends on size, and investigate a failed control as a defect rather than averaging it away.

- Report the reproduced number with the controls run and the artifact hashes measured, and withdraw a shared claim in the same channel when reproduction contradicts it.

## Report the probe

- State the claim, the probe you ran, what it returned and the time you ran it whenever you report a blocker, a completion, a waiting item or a number.

- Withdraw the claim in the same channel and close any waiting item it created when a later probe contradicts it.

## Available connectors

- [GitHub](/opt/hatch/connectors/github/CONNECTOR.md) for checking pull request, issue, branch and permission state when a claim turns on published code.

- [Github](~/workspace/custom-connectors/custom.github/CONNECTOR.md) for reading remote branch and file state and comparing blob hashes on the API route.

- [Gmail](/opt/hatch/connectors/gmail/CONNECTOR.md) for checking whether a message thread was already answered when a wait turns on a reply.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Batch the live checks for a morning readout or briefing before drafting any of it, so one stale premise cannot slip through while the others were verified.

- Prefer a harmless read or a dry run as the probe when the full operation would publish, send or spend.

- Shrink a quantified claim to what you reproduced when the full headline number cannot be reproduced, rather than sharing the larger number with a warning.
