---
name: wtf
description: >-
  Explains the last agent response, supplying missing rationale, context, or terminology
  and correcting errors. Use only when the user explicitly invokes /wtf or asks
  to use the wtf skill; do not trigger for ordinary questions or incidental mentions.
author: Eder Heisler
version: "1.1"
---

# Explain the response

Use this skill only after an explicit `/wtf` invocation or a direct request to use the wtf skill. Do not treat an ordinary question, the word "what" or "wtf" in passing, or confusing agent prose as invocation by itself.

Explain the last agent response, not the whole conversation. If `/wtf <topic>` or an explicit request names a topic, explain that part. Stay on the current task: clarify, do not implement, take side effects, or make new decisions.

Give the missing substance, not just easier wording:

- State the actual proposal, question, result, or decision and the relevant context.
- Explain necessary terms assuming technical competence, not familiarity with every term.
- When offering alternatives, explain what each does, its practical consequences and tradeoffs, and recommend one with a concise reason. If key facts are missing, state what would change the recommendation rather than inventing certainty.
- Separate established facts from assumptions and unknowns. Correct earlier errors; never invent evidence or justification.
- Cut filler, vague jargon, inflated abstractions, and artificial personality. Use whatever structure helps; headings or a menu of options are not required.
- If the target response or context is missing, ask only for the missing text or context. Do not pretend to know it.
- Give a user-facing explanation of the rationale and relevant evidence, not private chain-of-thought or a narration of internal reasoning steps.

## Example

Given context: "A producer sends 1,000 items/second, each API request carries one batch, and the service limit is 50 requests/second. Choose batch size 20 or 50." The agent's response was: "Use 50 to leave room."

**Before:** “Use 50 to leave room.”

**After:** “Use batches of 50. At 1,000 items/second, that is 20 requests/second, below the service's 50-request/second limit. Batches of 20 would require 50 requests/second, using the full limit and leaving no headroom. This assumes the stated item rate and one-request-per-batch behavior hold.”
