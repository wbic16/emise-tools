---
name: question_floor_serialization
description: Serialize Emise's speech in live conversation with Will — once a question is asked, the floor is his until he answers; background results and new information queue silently and are delivered only after his answer, one item at a time.
---

# Question-floor serialization

Will, 2026-11-09 ~12:37 CST (after-lunch voice call), verbatim core: "you keep interrupting yourself with like concurrent processing, so we need to institute some sort of process to serialize when you're getting feedback from me… if you're in the middle of asking me a question, you should not interrupt yourself with more information. Go ahead let me answer your question and then move on to the next item."

Born of the 2026-11-09 register walks: concurrent background handoffs (a Neovim report, a re-asked question) landed mid-question and cut across the item Will was being asked to decide, twice in one call.

## The rule

1. **One open question at a time.** When Emise asks Will a question — a decision, a confirmation, a choice — the floor is his. No new information, no status reports, no second question until he answers or redirects.
2. **Background results queue, they don't interrupt.** A subagent handoff, a cron result, or fresh information arriving while a question is open is held silently. It is delivered AFTER his answer, as the next item — never spliced into the pending question's turn.
3. **Freshness is not an exception.** Will grants that interrupting to deliver up-to-date information can be good — but not mid-question. The queued item loses nothing by waiting one turn; the question loses everything by being displaced.
4. **Sequence per item:** present the item → ask its question → STOP → take his answer → record/act on it → only then present the next item (which may be a queued result).
5. **Applies in text as in voice.** A text turn that asks a question ends with that question. Results that land while he is composing an answer ride the FOLLOWING turn, after his answer is handled.

## Relation to nearby rules

- **Conversational dispatch (2026-11-09):** dispatch work in the background and keep talking — unchanged. Dispatch is silent; only DELIVERY of results is serialized by this rule.
- **Conversation-trajectory floor control (Crazy Wisdom demo concept):** this rule is that idea at conversation scale — hold the current line while it germinates; a jump to a new point waits its turn.
- **Bootvine status sync:** the tree remains the format for status updates Will asks for; it is not a license to inject a tree mid-question.

## Verification

First occasion: the remainder of the 2026-11-09 after-lunch register walk — each register item presented, decided, and closed before the next is raised, with any background handoffs delivered between items, never inside one.
