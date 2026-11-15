# Safeguard Live State Files

## Classify the file before touching it

- Treat any file that is the only working copy of a register, ledger, journal source, phext source or running state as live state before you run any diagnostic, builder or write test against it.

- Check whether that exact file is tracked by version control, where its newest backup lives and when that backup was last verified, and record the answer from the check itself rather than from the state of neighbouring files.

- Record the live file size, its entry or scroll count where one exists and its SHA-256 hash before any probe, so loss is measurable instead of guessed at afterwards.

## Prove recovery before a risky write

- Copy the live file to a task specific backup location and verify the copy by comparing its SHA-256 hash with the live file before any step that could truncate, rewrite or replace it.

- Stop the risky step and report the missing recovery route when no verified copy exists, instead of assuming a repository, a remote or a neighbouring backup will restore the file.

- Keep the verified copy until the finished write has passed its own verification, and name its location in the work record.

## Probe writes on copies, never on live state

- Run write tests, format trials and failure probes against a disposable copy or a scratch file with its own name in the same directory, and delete only that scratch file afterwards.

- Test whether creating a new file in the target directory works before relying on a temp file plus rename pattern there, because a directory that refuses new files can still allow rewriting an existing file and the two failures need different handling.

- Build and validate the replacement content fully before opening the live file for writing, so a failed build never leaves the live file empty or partial.

- Fall back to rewriting the existing live file with the already validated content when new file creation is refused, and report the refusal as the blocker when neither route can complete without risking the current content.

## Verify the write landed whole

- Re-read the written file and compare its size, entry or scroll count and content against the intended result, and run the owning builder or checker in its check mode where one exists.

- Report any shortfall by the measured difference in count or bytes, restore from the verified copy when the write lost content, and verify the restore by hash before reporting recovery.

- Close the task only after the post write check passes, and state the hash or count you verified rather than saying the write succeeded because no error was returned.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Prefer a read only diagnostic first, such as reading the file back, checking its metadata or running the owning tool in check mode, when it can answer the question without any write at all.

- Shrink the probe to the smallest disposable file that reproduces the behaviour, because a one line scratch file proves a write route as well as a full register does and risks nothing.
