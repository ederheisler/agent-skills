---
name: wtf
description: >-
  Explains the last agent response or a named topic, supplying missing rationale, context, or terminology
  and correcting errors. Gives a short TL;DR by default; `full` gives details. Use only when the user
  explicitly invokes /wtf (or the harness's equivalent skill command) or asks to use the wtf skill;
  do not trigger for ordinary questions or incidental mentions.
author: Eder Heisler
version: "1.6"
---

# Explain the response

Use this skill only after an explicit `/wtf` invocation (below, `/wtf` also means the harness's equivalent skill command with the same arguments) or a direct request to use the wtf skill. An ordinary question, "what" or "wtf" in passing, or confusing agent prose is not an invocation; answer it normally.

## Target and limits

- Default target: the last agent response that is not itself a `/wtf` explanation, not the whole conversation.
- A topic or instruction after `/wtf` overrides the default: `/wtf explain topic A` means explain topic A using the relevant conversation context, not the literal words “explain topic A.”
- Right after a `/wtf` reply, `/wtf full` or a request for more details (the follow-up the footer offers) re-explains that reply's original response or topic in full. Never explain the `/wtf` reply or its footer.
- Only clarify: do not implement, take side effects, or make new decisions. Read-only lookups (reading files or docs, searching) are allowed to ground the explanation.
- If bare `/wtf` has no earlier agent response to explain, ask immediately which response or topic to explain; do not search other history. If a named topic's context is not in the conversation, look it up read-only first and ask only for what neither the conversation nor a lookup supplies. Never pretend to know it; label anything unverified as unverified.

## Content

Give the missing substance, not just easier wording:

- State the actual proposal, question, result, or decision and the relevant context.
- Explain necessary terms assuming technical competence, not familiarity with every term.
- When offering alternatives, explain what each does, its practical consequences and tradeoffs, and recommend one with a concise reason. If key facts are missing, state what would change the recommendation rather than inventing certainty.
- Separate established facts from assumptions and unknowns. Correct earlier errors; never invent evidence or justification.
- Cut filler, vague jargon, inflated abstractions, and artificial personality. Use whatever structure helps; none is required.
- Give a user-facing explanation of the rationale and relevant evidence, not private chain-of-thought or a narration of internal reasoning steps.

## Default TL;DR and `full`

`/wtf` gives a short explanation by default. `/wtf full` (or an explicit request for a full explanation) gives the detailed explanation using the guidance above, without the short-form limits below.

`full` or `--full` is the flag only as the standalone first argument; the remaining words are the target or instruction (`/wtf full explain topic A`, `/wtf --full topic A`). Elsewhere `full` is not a flag, but an explicit natural-language request for a full explanation still applies. To name a topic that starts with `full`, write `/wtf explain full stack`.

For the short explanation:

- Two to four sentences, at most about 80 words. No headings, bullets, or tables.
- If the response was wrong, lead with the correction. Otherwise lead with what was proposed or decided and the single reason that matters most; if options were offered, name the recommended one and why.
- Keep any assumption or unknown that would change the conclusion. If space runs out, drop terms, background, and secondary reasons first; never drop the correction, the decision or recommendation, or such an unknown. Short must not mean wrong or evasive.
- Define a term only when the response is unintelligible without it.
- After the TL;DR (not after a clarifying question), always add a separate line: “You can ask for more details or use `/wtf full`.”

## Examples

Context: "A producer sends 1,000 items/second, each API request carries one batch, and the service limit is 50 requests/second. Choose batch size 20 or 50." The agent's response was: "Use 50 to leave room."

**Default `/wtf`:** “Use batches of 50: that is 20 requests/second against a 50/second limit, so there is headroom; batches of 20 would use the whole limit. Assumes one request per batch.”

You can ask for more details or use `/wtf full`.

**Then `/wtf full` (same response):** “Use batches of 50. At 1,000 items/second, that is 20 requests/second, below the service's 50-request/second limit. Batches of 20 would require 50 requests/second, using the full limit and leaving no headroom. This assumes the stated item rate and one-request-per-batch behavior hold.”

**Correction-first:** the agent had said "Batches of 20 stay under the limit." Default `/wtf`: “Correction: batches of 20 make exactly 50 requests/second, which is the limit, not under it, so there is no headroom. Batches of 50 need only 20 requests/second. Assumes one request per batch.” Then the same footer line.

**Fresh session, `/wtf` first:** “No earlier agent response in this conversation. Which response or topic should I explain?” No footer.
