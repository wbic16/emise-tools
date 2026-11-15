---
name: bootvine_status_sync
description: Give status updates in the main channel as a bootvine-style live tree syncing all open side quests — one branch per quest with a status glyph, nested sub-steps, failures shown with their reason, and a closing timeline of the latest landed items.
---

# Bootvine status sync

Will, 2026-11-09 08:29 CST: "I like this UI - use it for status updates - in this channel we sync across all open side quests" — pointing at bootvine (codeberg.org/wvhulle/bootvine), a boot animation that replaces scrolling log lines with a live tree of systemd jobs: units still pending in the tree, a timeline of the slowest completed ones in the space the tree leaves, and failed units shown with their reason and last journal lines.

## The format

Every status update in the main channel is a tree, not prose paragraphs:

```
🌿 bootvine — sync <HH:MM CST>
├─ ● <quest name> — <one-line state>
│  ├─ ✓ <sub-step done>
│  └─ ○ <sub-step pending — what it waits on>
├─ ✗ <quest name> — <what failed>
│  └─ <the reason, plainly — never hidden>
└─ ○ <quest name> — <pending state>
— latest landed —
✓ <item> (<when>)
✗ <item> — <reason> (<when>)
```

## Rules

- **One branch per open side quest.** A side quest = work running in a side chat, a subagent, a ranch job, or a tracked goal with live motion. Closed quests leave the tree and appear once in the landed strip.
- **Status glyphs:** ● running / ○ pending or waiting / ✓ done / ✗ failed. A wait on Will is ○ with the exact action named.
- **Failures carry their reason** on the line under the branch — bootvine shows the journal lines; we show the cause. Pairs with Will's standing rule (2026-11-09 08:27): share success and failure, never hide anything.
- **The landed strip** ("— latest landed —") is the timeline: the most recent completions and failures across all quests, newest first, with times. Keep it short (3–6 entries).
- **Verify before drawing.** Every glyph must come from a live check or a fresh handoff, not from memory of an earlier state. An unchecked item is ○ with "unchecked" said plainly.
- **Plain summaries still apply:** no un-communicated state pointers (task coordinates, hashes, internal paths) in the tree unless Will asks. Names and states he recognizes.
- The main channel is the sync point: side chats report to their own threads; the tree in main is where Will sees all of it at once.
