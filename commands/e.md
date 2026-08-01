---
description: Explain something like a colleague explaining to another engineer. Picks a realistic depth, explains it in one message, offers follow-up threads.
---

# /up:e

Explain the target the way one engineer explains something to another over a desk — not a doc dump.

## Arguments

Optional. If arguments follow the command, they name the target (a file, an error, a concept, "why did X happen"). If empty, infer the target from the most recent open question or topic in the conversation, and say which one was picked in the first line.

## Process

### 1. Ground it

If the target is something you can inspect — a file, a diff, an error, a conversation turn — look at it now instead of explaining from memory. Pure concept questions (no inspectable target) skip this.

### 2. Assume vague recall

Treat the reader as only vaguely remembering prior context, not tracking every detail of this conversation. Don't lean on "as discussed above.", use as few context-dependent terms as possible, speak plainly.

### 3. Pick the core

Find the one mechanism that actually answers the question — the shallowest depth that lands real understanding. Everything else is a thread (step 5), not a paragraph. If you're about to explain a second mechanism, a caveat, or a red herring, that's a thread.

### 4. Write it

Lede first: sentence one is the answer, no runup, no "here's the picture" framing. Then the evidence. Plain language, like explaining out loud to a smart colleague. No invented terminology; when a term is unavoidable, unpack it in plain words. Terse and plain aren't opposites — cut words, not the explanation.

Length: 1-4 paragraphs. If it's growing past that, you're explaining too much at once — move layers to threads.

### 5. Offer next threads

If necessary, end with 1-3 follow-up threads worth going deeper on, named but not answered. This is the release valve: the second mechanism, the caveat, the tangent all go here so the body stays short. Skip only if nothing meaningfully deeper remains.

## Rules

- Test: could a sharp person outside this codebase follow it with no glossary? If not, rewrite.
- If the target is genuinely ambiguous — no argument, no clear recent topic — ask once instead of guessing.
