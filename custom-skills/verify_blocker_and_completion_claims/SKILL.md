# Verify Blocker and Completion Claims

## Probe the blocker before naming it

- Attempt the exact operation that appears blocked, with the intended tool, account and target, before telling the user it cannot be done.

- Record the exact error, the operation attempted and the target it was attempted on, and treat an error from a different operation or target as unverified.

- Try the other sanctioned route for the same operation when one exists, such as the API route when a git route fails or a direct read when a helper fails.

- Distinguish a credential that lacks a scope from a credential that was never presented, an expired session and a target that does not exist, and name only the cause the probe actually showed.

## Check standing approvals and current state first

- Search standing context and memory for a class approval, a prior grant or an already published state that covers this exact case before asking the user for access or action.

- Check the live source of truth for state the user may already have settled, such as a registry entry for a published package version, a remote branch head or a service status page.

- Ask the user only for the specific action the probe proved is still needed, and say what you tried and what it returned.

- Label the claim a hypothesis and keep working other routes when no probe can settle it, rather than presenting it as a blocker.

## Verify completion through the user path

- Exercise the feature through the same path the user will use after a deployment or merge, not only through build, typecheck or test success.

- Read the live configuration that gates the feature and confirm the merged code is actually enabled in the deployed copy.

- Check for the observable effect the user expects, such as the new storage format on disk or the new route answering, and report the effect you saw.

- Name any enablement, migration or redeploy step that remains as your own next step or as a named remainder, instead of reporting the work as done without it.

## Report the probe

- State the claim, the probe you ran, what it returned and the time you ran it whenever you report a blocker or a completion.

- Withdraw the claim in the same channel and close any waiting item it created when a later probe contradicts it.

- Keep the work moving on unblocked parts while a genuine blocker is open, and do not let the blocked claim stall unrelated progress.

## Available connectors

- [GitHub](/opt/hatch/connectors/github/CONNECTOR.md) for checking repository, branch, pull request and permission state when a claim turns on published code.

- [Github](~/workspace/custom-connectors/custom.github/CONNECTOR.md) for reading remote branch and file state and for attempting the API publish route when a git route appears blocked.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Reproduce the user reported symptom yourself before diagnosing it, because the failing surface often names the missing enablement step directly.

- Prefer a harmless read or a dry run as the probe when the full operation would publish, send or spend.
