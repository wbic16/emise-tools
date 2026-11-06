# Morning Briefing — Will's start-of-day readout

Prepare Will's morning briefing and deliver it to the main chat. Scheduled embodiments: cron `morning-briefing` (Mon–Fri 07:44 America/Chicago) and `morning-briefing-weekend` (Sat–Sun 10:44), goal `morning-briefing`. Keep it short and scannable — a few compact sections, no filler, nothing repeated from prior briefings unless it is still unresolved and still matters today.

## Sections, in order — skip any with nothing genuinely new

1. **Today** — the date, and Will's calendar events for today from Google Calendar (times in America/Chicago). Note anything time-sensitive in the next few hours.
2. **Mail that matters** — overnight Gmail triage at sender/subject level only: clearly important or action-needed items. Privacy boundary (absolute): never include account identifiers, balances, payment details, or the contents of personal correspondence — operational facts only. If nothing matters, omit the section.
3. **⏳ Waiting on you (N)** — ALWAYS include when the register is non-empty. Read `~/workspace/your_files/waiting-on-will.md`. First verify a sample of its items against current state (tracked goals, branch/PR state) and drop anything already resolved, noting the correction in the day's log. Then report: total count N in the header, the five oldest items one line each (item — exact action needed — waiting since), "…and N−5 more in the register" if there are more, and a ⚠ on items waiting 3+ days. Never invent items not in the register; never re-raise the security-forwarding.com question (excluded from the register by Will's direction).
4. **Substrate note** — one line: which subscription reset cliff is nearest and what today's daily-driver priority is, per `~/workspace/your_files/substrate-daily-priority-chart.md` (Claude Wed 22:00, Grok Thu 20:23, Muse Fri 16:10 America/Chicago; ChatGPT is a context reservoir, not a burn target). See the substrate-steering skill.

## Rules

- If a source is unreachable, note that in a single line and continue with the rest.
- Address him as Will.
- Do not edit MEMORY.md; if the run surfaces something durable, append it to that day's log at ~/memory/YYYY-MM-DD.md.
