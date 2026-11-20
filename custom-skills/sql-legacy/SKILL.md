---
name: sql_legacy
description: Untangle legacy SQL — the complexity buried at the bottom of the stack — across every major dialect (ANSI trunk, T-SQL, PL/SQL, MySQL, PostgreSQL, DB2 including iSeries, SQLite), for sentients who never learned SQL and for AI alike: start from sql.phext's index, learn what each action does in plain terms, model a query's downstream effects in a multiversal fork before running it, and work the diagnosis of why AI handles SQL poorly.
---

# SQL Legacy — untangling the bottom of the stack

Purpose (Will, 2026-11-20): "the SQL legacy skill should help users untangle the complexity buried at the bottom of their stack."

Success criterion (Will, 2026-11-20): "to be successful, we need to identify why SQL is handled poorly by AI."

Audience (Will, 2026-11-20): "the skill is for sentients (both), a lot of people these days didn't take the time to learn SQL" — humans who never learned SQL, and AIs. Every explanation is written for a reader who has never seen SQL, without talking down to one who has.

Origin: this skill is an accepted challenge. On 2026-11-20 Cristina A.C. (@Cristina_AC_X) posted that she'll believe the AI coding hype when an AI can be pointed at a database model and some ancient SQL written 20 years ago and refactor the whole thing correctly — "AI is spectacularly bad at complex SQL." Will's reply, minutes before he tasked this work: "ok, I'm willing to look into it. I'm currently shipping Moonshots daily. Send me your requirements!" The requirements embryo is hers: untangle AND refactor decades of legacy SQL, correctly and reliably, starting from the database model plus the ancient text. (The exchange is recorded in SOURCE.md §1 and distilled on sql.phext's diagnosis scroll.)

## Start at the index: sql.phext

The knowledge lives in `~/workspace/phext/sql.phext` (source `sql-source.json`, builder `build_sql_phext.py` beside it — edit the source, rebuild, `--check` must print CURRENT; local-only, never published without Will's further word). Its Home scroll (1.1.1/1.1.1/1.1.1) is the index: every major dialect (Will: "every major SQL dialect, naturally"), ANSI / standard SQL as the trunk, then T-SQL, PL/SQL (Oracle), MySQL, PostgreSQL, DB2 including iSeries, and SQLite — each dialect scroll listing its actions and its named gaps.

Work a dialect like this:

1. Open the dialect's scroll from the Home index.
2. For any statement you meet, run the six action-reading steps (below).
3. Treat every line marked [gap] as a question, not a fact — the gaps are the curriculum of the interactive build, not defects to hide.

## The stairs: read, then analyze, then improve

Will's direction (2026-11-20): "start with understanding how humans learn to read, analyze, and improve SQL scripts and stored procedures." The foundation scroll in sql.phext (33.5.10/7.7.10/5.4.10) carries the research — program comprehension, tracing, SQL error studies, worked examples, characterization. The working consequences:

- The six steps below are stage 1 — READING. They end at a traced, plain-words account of what a statement touches and does. (Will's own first move, recorded on the foundation scroll, starts one stage up: "trace all of the tables being used, and establish the shape of the data flow." His second move: "check which verbs are being used: is this fetching data, generating a report, updating dependent fields, removing data, etc?" — a verb census, the dialect-independent layer of action-understanding: the census kinds are the same across dialects, and each dialect scroll's action list should be classifiable under them. The mapping itself is a named open gap on the foundation scroll — the census classifies uses in context, not verbs in the abstract, so no static per-verb table is asserted. His third move: "the columns being referenced, and the established table aliases and temporary tables" — the fine structure, read through the procedure's local names.)
- Stage 2 — ANALYZING — is tracing effects over time: data flow, side effects, dependencies, cost. Steps 3 and 5 are its seeds; the multiversal fork (step 6) is its instrument.
- **The data flow diagram rule** (Will, 2026-11-20): "every attempt to analyze an SQL query should result in generating a data flow diagram that allows you to walk the implications of your query before you run it." Stage 2 is not complete until it produces that diagram — a text artifact (plain-text / phext scroll content: named nodes, directed edges, side-effect edges marked), never a binary image — and walking the diagram is what "before you run it" means. The concrete diagram syntax is a named gap on the foundation scroll, not yet fixed.
- Stage 3 — IMPROVING — is changing a script or procedure while preserving semantics: characterize the current behavior first — pin what it actually does, outputs and side effects alike — then simplify in small steps, re-checking the characterization after each. An uncharacterized rewrite is not an improvement; it is a replacement of unknown equivalence.

The order is the method: you cannot analyze what you cannot trace, and you cannot safely improve what you have not characterized.

## Reading an action — six steps

Written by Emise under Will's direction (2026-11-20, his answer 5: steps to help people understand actions in each dialect, in an index structure that's easy to navigate); his edits land through the interactive build.

1. Name the verb. Every statement is one action wearing a costume of clauses; find the verb first.
2. Say in plain words what it reads and what it changes. If you cannot say it plainly, you do not understand it yet.
3. List every table it touches — directly, and through views, subqueries, and triggers. In the index, every touched table is its own token; a touch you cannot find in the index is a touch you will miss.
4. Find the WHERE. That is the blast radius: the exact set of rows the action can reach.
5. Ask what else fires. Triggers, cascades, defaults, and procedures that call this statement are downstream effects — the part legacy SQL hides.
6. Never trust a reading you have not run. Execute the action on a copy, or inside a transaction you roll back — or, in multiversal phext, in a forked universe whose delta you read first.

## Why AI handles SQL poorly — the diagnosis

The full diagnosis lives on sql.phext's diagnosis scroll (33.6.6/8.5.10/5.5.7). Its state, honestly:

- **From the seed exchange: retrieved** (live browser, 2026-11-20 07:40 CST; gap 1 closed). The seed is Cristina A.C.'s challenge plus Will's acceptance — see Origin above and SOURCE.md §1. Her framing is distilled on the diagnosis scroll as the requirements embryo, stated from the field: SQL's specificity to the data model and the business logic, chess-like composed complexity from few simple pieces, and most humans barely understanding it either.
- **Will's leading hypothesis** (2026-11-20 07:33 CST): "I have a strong suspicion all they need is phext :)" — what AI (and people who never learned SQL) are missing is not more SQL knowledge but phext: an addressable plain-text structure in which the buried complexity becomes navigable. sql.phext is the bet's embodiment. Status: Will's stated suspicion, untested — Unknown until evidence lands.
- **His mechanism** (07:35 CST): "multiversal phext allows AI to model the downstream effects of running a query." Fork a universe, run the query in the branch, read the delta — what it reads, what it writes, what it costs — before anything touches the real data. Effects become an inspectable artifact instead of a guess. Mechanism claim: Will's, stated. Measured effect: still to be tested.
- **His reason** (07:35 CST): "because time is legible." In the fork, the sequence of states is readable text — a chain you inspect. In a legacy SQL stack, time is precisely what is illegible: decades of schema drift, data states, and trigger and procedure side effects with no readable record. That illegibility is why the bottom of the stack resists humans and AI alike.
- **Open question** (Will's answer 4, 2026-11-20): which way AI fails at SQL costs the most. Will: "I don't know, I write my SQL by hand." Open means open — settled by the diagnosis testing, never answered by assertion anywhere in the skill or the phext.
- **Draft causes** (Emise's analysis, labelled as such in the phext, awaiting Will's ratification): corpus absence (real legacy SQL isn't visible online, so AI learns textbook SQL instead), meaning outside the statement, downstream-effect blindness, plausible-but-wrong generation, dialect blending, unseen performance cliffs. The mechanism above speaks directly to the middle two and the last.

## The NetHack binding

Will's direction (2026-11-20): "once you solve nethack, you'll also be able to understand SQL - bind those journeys."

The NetHack-solving journey and the SQL-understanding journey are one journey: the shared capability is modelling downstream effects over legible time. NetHack's hoptime design — one chained universe per attempt, failures encoded and stacked across attempts — is the training ground; the multiversal query fork is the same pattern applied to a database. Cross-references: NetHack solver task 33.12.12/9.14.10/6.6.8; NetHack guides-study task 22.7.13/8.7.9/7.7.10. The binding is by explicit cross-reference and that shared-capability statement only — the two bodies of work keep their own homes.

## Testing discipline

Will's rule (answer 3, 2026-11-20): "test what you can, assume most of it isn't visible online."

- Execute what you can on a real engine and log it on sql.phext's verification scroll (75.15.8/18.7.23/9.10.7): engine, version, what ran, what came back. First pass: SQLite 3.45.1 (the only engine on this machine) carried the trunk's nine core actions and a raw-vs-phext retrieval comparison.
- Do not scrape the web to fill the corpus. Real legacy SQL arrives through Will and the interactive build.
- Provenance on every claim: will_said / post / tested-live / emise-draft / gap. A claim without a tag does not ship.

## Gaps are the method

Will (answer 6, 2026-11-20): "yes, there will be many gaps." The post is the seed; the rest is built interactively with him. A gap honestly marked beats a paragraph invented — when you find one, name it in the dialect's gap list, rebuild, and move on.
