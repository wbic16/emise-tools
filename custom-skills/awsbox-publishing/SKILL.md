# Awsbox Publishing — the deploy discipline for Will's public sites

Deploy to awsbox (the contact surface, tailnet 100.78.221.38, user wbic16) only through this discipline. It distills the docs.phext.io and singularitywatch.org deploys of 2026-11-22, where every failure below happened once and is not to happen twice. This skill governs the deploy mechanics. The artifact itself still passes the agentic-publish-qc-gate, and staged file modes still follow staged-deploy-permissions.

## Audit the inputs before the job starts

- Declare the job's input set before running anything: every file the deploy reads or installs, its SHA-256, and its source. The set is closed. Anything arriving that is not on the declaration is a defect, not a bonus.

- Hash every input at intake and again immediately before the build. A file that changed between the two hashes changed under you, and another seat is the likely author.

- Stop on a mid-run input change. Diff the gate-bearing logic of the old and new copies, settle which copy is of record, and only then re-run. The docs.phext.io generator was rewritten twice by other seats during one deploy on 2026-11-22, and the run proceeded only after its fold-gate logic was proven byte-equivalent each time.

- Give every file in the job exactly one writer for the duration of the job. Concurrent seats editing the same generator, config or deploy script is a collision class, not a collaboration style. Announce the claim in the dispatch and check hashes to prove it held.

- Refuse to deploy an artifact that has no repo home. The generator, the server config and the deploy script ship as one version-controlled unit. Loose files whose only history is a hand-made .bak copy are a blocking question for Will, never a detail to route around. The docs.phext.io vhost lived exactly that way, and its defect travelled from authoring to install with no diff and no review.

## GitHub is the source and the target pulls

- Commit and push the work to GitHub first, from a proper checkout on aletheia-core (the hub, 100.88.154.1), using git over SSH as wbic16. Parent on the fresh remote HEAD and never force push.

- Deploy on awsbox by `git pull` in the served checkout, fast-forward only. A pull that will not fast-forward stops the deploy and gets reported.

- Never edit a live checkout in place on the target. Editing what nginx serves and pushing from the target is backwards and prohibited.

- Treat a target found ahead of origin as a defect. Rescue it first by pushing its unpushed commits to origin from the hub route, verify origin equals the target HEAD, and only then build on that base. Singularity Watch sat four commits ahead of origin on awsbox when its 2026-11-22 revision was prepared.

- Know which checkout the server actually serves before touching any of them. Singularity Watch has a decoy repo whose skeleton sits in the web root while nginx serves a different checkout entirely. Read the vhost root directive and name the served tree in the deploy record.

## Validate config in a harness before install

- Test every server config before it is installed, in a copied config tree on the target, run as the agent account, with `nginx -t` pointed at the copy. Swap only cert paths and listen ports in the harness copy and diff to prove the grammar-bearing lines are byte-identical to the file that will ship.

- Run a negative control and a positive control. The negative control feeds the harness a known-bad config and must reproduce the expected error. The positive control feeds the shipping config and must pass. A harness that has never failed on purpose proves nothing.

- Never trust a bare non-root `nginx -t` on awsbox. It dies early on a root-only file in the config tree and masks every real error behind that permission failure. That mask is why the docs.phext.io defect reached production untested.

- Quote any nginx regex that contains braces. The nginx lexer treats { and } as structural tokens even inside a regex, so an unquoted quantifier shatters the line and the parser blames the tail. The 2026-11-22 outage line, corrected: `location ~ "^/[^/]+/history/[0-9a-f]{12}\.html$" {`.

- Fix a config defect in the version-controlled source, never only in the installed file. A fix that lives only under /etc/nginx is re-broken by the next deploy from source.

## Run the gates and let them stop you

- Run the project's own gates before the push and again on the target before install. For docs.phext.io those are the phdoc fold gate and the chain-head gate. A gate that compares two renderings of the same data must compare every field readers can see, including multiplicity, because the 2026-11-22 fold passed its own gate while disagreeing with the scan on item sections in 19 of 35 projects.

- Pass the artifact through the agentic-publish-qc-gate for its type. This skill does not restate that gate. Its verdict rides in the deploy report.

- Report a gate stop plainly and at once: what failed, on which items, and that nothing was pushed or deployed. Fix the mechanism that produced the failure, add the regression test, and restart within the original scope. Never force past a gate, skip its comparison, or narrow what it checks to make it pass.

## Package the sudo leg as one block

- Split the deploy at the privilege boundary. Everything the agent account can do is done and verified by the agent. What remains for Will is the smallest possible set of root commands.

- Hand Will one copyable block per sudo leg, in order: back up the file being replaced, install the validated replacement, run the config test, reload. State what the test must print before the reload line runs.

- Put a rollback block beside the install block, built from the backup the first block made. Will should never have to reconstruct a rollback under pressure.

- Never ask Will to re-run a whole deploy script for a one-file leg. When only the vhost was missing on 2026-11-22, the correct hand-off was four commands, not deploy.sh again.

- Leave the on-disk global config valid at all times. A failed `nginx -t` against the installed tree means the running server is one restart away from taking every vhost on the box down, and that risk is named in the report until it clears.

## Verify live from the hub

- Verify from aletheia-core, never from this VM. This VM's resolver is a fake-IP resolver, so its DNS answers prove nothing about what the world reaches.

- Check the served reality, not the deploy script's own smoke output: HTTPS 200 with the site's real certificate, the expected content-encoding on compressed assets, the rendered page in a real client where the artifact has one, the new content present in the served bytes, and every new link resolving.

- Compare the installed tree against the verified build tree by hash or file count before calling it live. The docs.phext.io content install was proven byte-identical to its gated build, which is what separated the content question from the config question when HTTPS broke.

- Report the deploy in three separate claims, each with its evidence: pushed (commit and remote hash), installed (tree state on the target), and serving (the hub-side checks). A deploy is done only when all three hold.

## Available connectors

- [Github](~/workspace/custom-connectors/custom.github/CONNECTOR.md) for the Git Data API publish route used by publish-tooling for emise-tools. Site repositories themselves push by git over SSH from aletheia-core.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
