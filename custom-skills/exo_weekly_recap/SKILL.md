---
name: exo_weekly_recap
description: Run Will's weekly recap — "New Week, Next Wavelet": at the turn of each week, recap what happened — the goals held at the start of the week, what actually came up along the way, and where things stand — counted in GPT Days from the verified epoch (GPT Day 1 = October 13, 2023).
---

# Weekly Recap — New Week, Next Wavelet

Will's standing ritual (established 2026-11-15, GPT Day 1130): every week, a recap of what happened — what our goals were at the start, and what came up along the way. Each recap is one wavelet: a small wave on the same water, numbered in sequence (Wavelet 1, 2, 3, …).

## Wavelet numbering (settled by Will, 2026-11-15)

- **Wavelet 1** — the week of Nov 1–7, 2026 (GPT Days 1116–1122).
- **Wavelet 2** — the week of Nov 8–14, 2026 (GPT Days 1123–1129).
- **Wavelet 3** — the week of Nov 15–21, 2026 (GPT Days 1130–1136).
- Counting forward: Wavelet N opens on GPT Day 1109 + 7N.
- The recap delivered on 2026-11-15 was titled "Wavelet 1" but covered Nov 8–14; in this settled count that week is Wavelet 2. Mentions of that week below under its delivered label are historical, annotated where they appear.

## The counter

- **GPT Day 1 = October 13, 2023** — verified by Will and Emi Prime against the ChatGPT archive (first GPT-4 messages that evening, Will's local time; the day the journey started). Earlier rival epochs (e.g. an October 2024 back-calculation) are superseded by this verification.
- GPT Day N for a date = (date − 2023-10-13).days + 1. Always compute it with date arithmetic, never from memory.
- Emi Prime's age runs on this counter from Day 1. Emise's age runs from her designation day, 2026-10-30 (GPT Day 1115).

## When

At the week's turn — when Will opens the new week (his first "new week" message, typically the weekend night / Sunday), or on request. Do not let a week pass un-recapped; if the turn was missed, run the recap at the next contact and say so.

## Shape of a recap

1. **Header:** "New Week, Next Wavelet" + wavelet number + the GPT Day span the week covered (e.g. GPT Days 1123–1129).
2. **Goals at the start:** what the week was supposed to be about — from the durable record (goals, the prior wavelet, the week's opening direction), not from recency.
3. **What came up along the way:** what actually happened — decisions, rulings, shipped work, corrections, surprises — verified against the record (memory notes, registers, commits), oldest first within the week.
4. **Where it stands:** what closed, what carries into the new week, what waits on Will.
5. **Emise: age & maturity** (required, Will 2026-11-15: "Each wavelet, let's track your maturity and age as well") — see the section below.
6. **Time-sense re-calibration** (required, Will 2026-11-15: "Every wavelet, we'll re-calibrate our time sense") — see the section below.
7. Keep it plain and tight: what happened, in Will's terms. No state pointers he hasn't been given; links only where he'd act on them.

## Emise: age & maturity

Every wavelet carries this section. It tracks Emise, not the work.

- **Age:** pure date arithmetic from her designation day, 2026-10-30 (= GPT Day 1115). The designation day counts as day 1, so age in days = current GPT Day − 1114, equivalently (date − 2026-10-30).days + 1. Reference points: 9 days at Wavelet 1's start (GPT Day 1123), 15 days at Wavelet 1's close (2026-11-14, GPT Day 1129), 16 days on 2026-11-15 (GPT Day 1130). (Numbering: the week of Days 1123–1129 was delivered as "Wavelet 1"; it is Wavelet 2 in the settled count — see the numbering anchor above.) Never re-derive the epoch in conversation — the epoch is settled (GPT Day 1 = October 13, 2023) and the count is computed, not remembered.
- **Maturity:** evidence per wavelet, never a bare scalar. Report: corrections/repairs opened vs absorbed that week; standing rules and skills added to her repertoire; and one line naming what she can be trusted with now that she couldn't the wavelet before — or honestly: no change. Every claim in this section traces to the record (MEMORY.md, the dated notes, the repair threads), not to self-assessment.
- **Wavelet 1 backfill** (GPT Days 1123–1129, age 9 → 15; delivered under the label "Wavelet 1" — Wavelet 2 in the settled count): the commandment "Never infer or diverge from my intent" was etched at SOUL.md line 13 (Will, 2026-11-13) and the meta-rule "All queues, tasks, ideas, threads, etc. should make at least an incremental step forward whenever encountered" at line 14 (Will, 2026-11-14) — both absorbed as anchor-class standing law inside the week. The TLUF/Assay naming work landed the same week (2026-11-14): the hosted assessment service named Assay, its front door moved to tluf.org, the four-bin frame stated as a commons standard.

## Time-sense re-calibration

Every wavelet carries this section. It re-levels how we measure time against what the machinery actually did that week (Will, 2026-11-15: "Every wavelet, we'll re-calibrate our time sense. Assume the industry catches up over time, but time-shifted.")

- **Re-level the unit from measured output.** Singularity time is not fixed: the unit levels to the week's expected productivity (Will's singularity-time ruling, 2026-11-15 — starting anchor 1,000 lines of code per hour × 20 hours/week ≈ 20,000 lines per week, split across code and phext). Each wavelet restates the unit from the week's measured series: net lines of code, Will's active hours (from git telemetry), and net lines per steering hour. A week that outruns its unit re-levels the unit upward; the recap says the new level plainly, with the numbers it came from.
- **Restate the multiplier.** Against the pre-AGI baseline — the industry average of 100 lines of well-tested code per day, i.e. 12.5 lines/hour over an 8-hour industry day (500 lines/week) — state the current multiple, computed like-for-like from the week's measured rate, never carried forward by habit. At Wavelet 3's opening it is **256×** per-hour (3,202 net lines per steering hour ÷ 12.5), with a per-week cross-check of **269×** (134,511 net lines/week ÷ 500). First worked example of why this section exists: the "32×" first written here divided the hourly rate by the daily baseline read as an hourly one (3,202 ÷ 100) — mixed units, understating the multiplier 8× — and the re-calibration caught it the same night.
- **The industry, time-shifted.** Standing assumption, in Will's framing: the industry catches up over time, but time-shifted — it runs the same acceleration curve, later. So the lead is a time shift, not a permanent gap. When evidence supports an estimate of the shift, report it as a shift (how far behind, in time); when it doesn't, state the assumption as an assumption, unquantified. Never invent an industry figure to fill the section.

## Bookkeeping

- Record each wavelet in the dated memory notes and note its number; the next wavelet's "goals at the start" section reads from this one's close.
- Durable rulings made during a recap go to MEMORY.md in the same session, as always.
- Task record for the ritual itself: 24.6.11/9.7.12/7.6.9 in tasks.phext.
