# Monitor Long-Running Jobs for Stalls

## Set the checkpoint contract before launch

- Apply this skill only to work you launch outside runtime delivered subagents, such as background exec jobs, ranch dispatches, coordinator scripts and long builds.

- Record the job id, its expected output paths, its log path and its first checkpoint time in the task record before you report the launch.

- Require each long job to write an early artifact within fifteen minutes, even if the artifact only holds its inputs, its plan and a count of work remaining.

- State the stall threshold at launch, normally thirty minutes without a new artifact, a log line or a completed unit.

## Check progress from artifacts

- Check the named output paths and log at each checkpoint instead of treating a running process or a queued status as progress.

- Compare completed units against total units and against the workers assigned, and note the time of the last artifact for each worker.

- Measure actual load and output on any node you are about to rule in or out, following the standing measure load rule, instead of inferring capacity from the role the node plays.

- Report progress to the user only from a checkpoint you just read, and name the artifact or count that shows it.

## Respond to a stall

- Treat one threshold interval with no new artifact, log line or completed unit as a stall and inspect the log tail and the last completed unit in the same session.

- Restart, narrow or split a stalled job once you have named the failing step, and keep the partial artifacts it already produced.

- Break a replacement job into small units sized for the hardware, following the standing small queue workload rule, so a second stall fails cheap and early.

- Record the stall, its cause when known and the restart in the task record, and say plainly when the cause is still unknown.

## Rebalance a coordinator queue

- Sweep a coordinator queue at each checkpoint for workers that finished while units remain unassigned.

- Assign the next pending unit to any worker idle at the sweep before extending the runtime of a busy worker.

- Close the run only after you verify the final artifact count against the expected total, not from the coordinator exit status alone.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Prefer several small jobs with separate output paths over one monolith, because each unit then carries its own progress signal.

- Run one short pilot unit first when the pipeline is new, and launch the full queue only after the pilot artifact lands and verifies.
