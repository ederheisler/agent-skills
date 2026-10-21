---
name: wtf
description: >-
  Explains the last agent response or a named topic, supplying missing rationale, context, or terminology
  and correcting errors. Defaults to TL;DR; optional `full` flag gives details. Use only when the
  user explicitly invokes /wtf or asks to use the wtf skill; do not trigger for ordinary
  questions or incidental mentions.
author: Eder Heisler
version: "1.5"
---

# Explain the response

Use this skill only after an explicit `/wtf` invocation or a direct request to use the wtf skill. Do not treat an ordinary question, the word "what" or "wtf" in passing, or confusing agent prose as invocation by itself.

By default, explain the last agent response, not the whole conversation. Accept a topic or natural-language instruction after `/wtf`: `/wtf explain topic A` means explain topic A using the relevant available conversation context, not the literal words “explain topic A.” A named topic overrides the last-response default. Stay on the current task: clarify, do not implement, take side effects, or make new decisions.

Give the missing substance, not just easier wording:

- State the actual proposal, question, result, or decision and the relevant context.
- Explain necessary terms assuming technical competence, not familiarity with every term.
- When offering alternatives, explain what each does, its practical consequences and tradeoffs, and recommend one with a concise reason. If key facts are missing, state what would change the recommendation rather than inventing certainty.
- Separate established facts from assumptions and unknowns. Correct earlier errors; never invent evidence or justification.
- Cut filler, vague jargon, inflated abstractions, and artificial personality. Use whatever structure helps; headings or a menu of options are not required.
- If the target response or context is missing, ask only for the missing text or context. Do not pretend to know it.
- Give a user-facing explanation of the rationale and relevant evidence, not private chain-of-thought or a narration of internal reasoning steps.

## Default TL;DR and optional `full` flag

`/wtf` gives a short explanation by default. `/wtf full` (also `/wtf --full` or an explicit request for a full explanation) gives the detailed explanation using the guidance above, without the short-form limits below. The flag combines with a topic or instruction: `/wtf full explain topic A`.

For the default short explanation:

- Two to four sentences, roughly 80 words at most. No headings, bullets, or tables.
- Lead with what was proposed or decided and the single reason that matters most. If options were offered, name the recommended one and why.
- Define a term only when the response is unintelligible without it.
- Keep corrections and any assumption or unknown that would change the conclusion; drop everything else. Short must not mean wrong or evasive.
- After the TL;DR (not after a clarifying question), always add a separate line: “You can ask for more details or use `/wtf full`.”

## Example

Given context: "A producer sends 1,000 items/second, each API request carries one batch, and the service limit is 50 requests/second. Choose batch size 20 or 50." The agent's response was: "Use 50 to leave room."

**Before:** “Use 50 to leave room.”

**Default `/wtf`:** “Use batches of 50: that is 20 requests/second against a 50/second limit, so there is headroom; batches of 20 would use the whole limit. Assumes one request per batch.”

You can ask for more details or use `/wtf full`.

**With `full`:** “Use batches of 50. At 1,000 items/second, that is 20 requests/second, below the service's 50-request/second limit. Batches of 20 would require 50 requests/second, using the full limit and leaving no headroom. This assumes the stated item rate and one-request-per-batch behavior hold.”
