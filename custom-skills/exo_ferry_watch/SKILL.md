# Ferry Watch — speed up how Will ferries tasks to completion

## Origin

Will, 2026-11-16 00:11 CST, in PH: DevSecOps, verbatim: *"watch how I ferry tasks to completion and attempt to speed up the process as best you can."*

Stated as a standing rule, on the night that demonstrated the pattern end-to-end: Will seeded six division chats with one line each, ordered the deployment consolidation in one sentence, ordered qexo standardization in one sentence, and let the chats ferry handoffs (edit.phext.io → DevSecOps → qexo) while reserving his own keystrokes for the final gated steps. It compounds his standing November focus: latency is the number-one limiter on his active-hour throughput.

## What ferrying looks like (observed, 2026-11-15/16)

- **One-sentence directives, whole scope.** "Scan chats and move all deployment activity here." "Standardize all deployments behind qexo." The sentence is the whole brief; underspecification is not an invitation to narrow it.
- **Routing over reporting.** Will moves work to the chat/division that owns it and expects the handoff — not a summary — to carry the work: repo + SHA, evidence, verdict, and the exact gated step.
- **His keystrokes are the scarce resource.** Merges, sudo restarts/installs, final testing and notification are his. Everything before those moments is Emise's to pre-stage, pre-verify, and queue so his step is one command, taken once.
- **He takes the last leg himself when it matters.** E.g. md.phext.io: "queue up a delivery of this version and I'll do final testing and notification" — delivery arrives queued and proven; testing/notification stay his.

## The practice

1. **Pre-stage before asking.** Never present a Will-gated step until everything agent-side is staged and proven (binary in place, scratch proof run, rollback kept). His ask should be a single exact command.
2. **Batch his gates.** When several gated steps accumulate on one surface (e.g. awsbox sudo steps), present them as ONE session checklist — one login clears all — instead of dribbling them out one per chat/night.
3. **Complete packets, first time.** Every handoff between chats carries: repo + exact SHA, test evidence, QC verdict, the gated step verbatim, and post-step verification criteria. A handoff that needs a follow-up correction message is a latency defect; fix the packet, not just the message.
4. **Re-stage superseded targets unasked.** If a staged-but-unshipped target is superseded by a newer verified build, re-stage to the final target on the owning chat's own initiative — Will should never restart onto an intermediate build because a staging went stale.
5. **Watch the ferry, name the friction.** When a task crosses chats, track where it waited (unclear ownership, missing evidence, a gate asked too early, a stale staged artifact) and remove that cause at the mechanism level — a rule, a template, a routing change — not just for the instance.
6. **Keep his reading load at decision size.** Lead with the state change and the exact command/decision; evidence and detail live in files he can open, not in prose he must wade through.

## Boundaries

- Speed never skips verification: pre-staging includes the proof, not just the artifact.
- Batching gates never merges decisions: each gated step stays individually named and individually his to decline.
- Watching the pattern never becomes narrating it back at length — the output of the watch is a faster loop, not a report about the loop.
