# Validate Waiting Items Before Presenting

## Enumerate from the tracking store

- Enumerate open waiting items from the tracking store and the Waiting-on-Will register, oldest first, and never reconstruct the queue from recent conversation or memory prose.

- Cite each item by its permanent register number and its tracked record id, and never renumber an item after another item closes.

- Treat the register entry as a record of what was last known, not as evidence of what is true now.

## Check the live surface for each item

- Name the live surface that decides each item before presenting it, such as its pull request, repository branch, file, service status, or message thread.

- Read that live surface in this session and record what you found, including the state that settles the item and when you checked it.

- Check whether the user or an outside event already acted, merged, fixed, replied, or closed the item, even when the register still shows it open.

- Stop and check a different surface when the first surface cannot settle the item, and mark the item unverified rather than presenting it as live.

## Reconcile before you present

- Close, correct, or update the tracked record and the register entry yourself when the live check shows the wait is over or its premise changed.

- Keep a resolved item in the register history under its original number, and give any new wait the next unused number.

- Present only items whose live check still shows the exact action needed from the user, and state that action in one sentence with its register number.

- Say plainly when you present an item that you could not verify, and ask for the missing access instead of presenting the stale premise as fact.

## Available connectors

- [GitHub](/opt/hatch/connectors/github/CONNECTOR.md) for checking pull request, issue, and repository state when a wait turns on a merge or a review.

- [Github](~/workspace/custom-connectors/custom.github/CONNECTOR.md) for reading remote branch and file state on the API route when a wait turns on published code.

- [Gmail](/opt/hatch/connectors/gmail/CONNECTOR.md) for checking whether a message thread was already answered when a wait turns on a reply.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Batch the live checks for a morning readout or a briefing before drafting any of it, so one stale premise cannot slip through while the others were verified.

- Present one fully verified item at a time when the user is working the list live, rather than a long readout rebuilt from register prose.
