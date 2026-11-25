# Review PR Composition

## Build the dependency map

- List every open pull request in the set before reviewing any one of them, with its full URL, base branch, head revision and stated purpose.

- Mark the pairs that touch the same files, the same symbols, the same pinned revision or the same runtime path, and treat each marked pair as related even when their titles sound unrelated.

- Record which pull request supplies a revision, symbol or route that another one pins or calls, because that supplier is a merge order constraint and not a preference.

## Test the composed tree

- Build one scratch tree that applies the related pull requests together in the proposed order, instead of trusting that each branch passing on its own means the set passes.

- Run the full test suite of the composed tree and at least one live path through the combined behavior, such as a request that crosses an authorization rule added by one pull request and a route added by another.

- Check error behavior on the composed tree as well as success behavior, because a composition fault can turn an expected refusal into a server error or hide records that a filter in one pull request was meant to expose.

- Inspect the composed diff for work that no single pull request title announces, such as an extra build step or a lockfile change that contradicts the stated scope, and flag it as fix first rather than merging around it.

## Report merge order and verdicts

- Give each pull request one verdict of merge, hold or fix first, and state the evidence for that verdict from the composed tree rather than from the single branch.

- State the merge order as a numbered sequence that puts every supplier pull request before the pull requests that pin or call what it supplies.

- Keep the review in an internal ledger when the review was done by a facsimile or a delegated reviewer, and post nothing to the pull requests themselves without the user directing it.

- Re-run the composed test after any pull request in the set changes, because a new head revision invalidates the earlier composition result.

## Available connectors

- [GitHub](/opt/hatch/connectors/github/CONNECTOR.md) for reading pull request diffs, revisions and merge state.

- [Github](~/workspace/custom-connectors/custom.github/CONNECTOR.md) for repository file and tree operations through the registered API.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Review a single isolated pull request on its own branch when the dependency map shows no shared files, symbols, pins or runtime paths with any other open pull request.

- Ask the user to choose between merging a subset now and holding the rest when the composed tree passes only for that subset and the remaining order is a judgment call.
