# Staged Deploy Permissions

## Normalize modes at staging time

- Set directory modes to 755 and regular file modes to 644 on every staged web tree before it is copied, installed or served.

- Run the normalization as a step inside the staging or install script itself, never as a remembered manual fix after a failure.

- Keep executable bits on scripts that must run, setting them to 755 explicitly instead of relying on the mode they were staged with.

- Leave secret files out of the web tree entirely, and keep any secret a deploy must stage at 600 in a location the web server does not serve.

## Verify as the server reads

- Read one staged file back as the serving user, such as the nginx or web server account, before running later install steps like certificate setup or HTTPS configuration.

- Fetch the staged entry page over HTTP from the target host and confirm it returns its real content, not a 403 or a permission error page.

- Stop the install at this check when either read fails, fix the modes, and rerun the check before continuing to any later step.

- Record the modes found, the normalization applied and the serving user read result in the task record for the deploy.

## Report the deploy state

- Report a deploy as installed only after the serving user read and the HTTP fetch both pass on the final staged tree.

- Name a permission failure as a staging defect in your own step when one is found, and state which later steps have not run yet because of it.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Set a restrictive umask deliberately in the staging script and then normalize from it, so the output modes do not depend on which shell or agent staged the files.

- Add the serving user read check to the deploy smoke test that already runs, so the permission gate rides a check that happens on every deploy rather than a new one that can be skipped.
