> **DRAFT written by the assistant — review and edit before relying on it.**

# LinkedIn Self-Learning System

Companion to every other file — this is the method layer for Part 57 of the spec. It says what gets recorded after a post, when a review happens, how a finding earns the right to become a rule, and how that finding is written into `LINKEDIN_LEARNING_MEMORY.md`.

`LINKEDIN_LEARNING_MEMORY.md` is the data. This file is the process. Neither works alone: a memory file with no recording discipline is a diary, and this process with no memory file repeats the same mistake every 9 posts.

**Hard rule:** nothing in this system changes on faith. A preference stated in any other file stays a preference until this file's process confirms it against real results. A hypothesis is not a finding.

---

## What this governs, and what it doesn't

**Governs:** per-post recording, batch design, review cadence, confidence levels, how findings get promoted into memory, how experiments are opened and closed.

**Doesn't govern:** what to post (Operating System), when to post (Scheduling System), hashtag selection, commenting on other people's posts (Comment Intelligence), or the pre-publish gate (Verification Gate). This file consumes their outputs; it doesn't overrule them.

**Policy:** nothing here authorizes scraping, browser automation, bots, or third-party analytics tools. Metrics are read from LinkedIn's own post/profile analytics and recorded by hand by Umesh. If a number isn't visible there, it isn't a number.

---

## Layer 1 — record after every post

Recorded per post in the **Content Database** sheet of `linkedin_content_system.xlsx`, in the row for that post.

| Field | Source | If missing |
|---|---|---|
| Date + time published | Actual publish time | — |
| Slot (TOFU / MOFU / Authority) | The batch that produced it | — |
| Series (01-07) | Operating System | — |
| Hook type used | The post itself | — |
| Format (text-only, visual, list, story) | The post itself | — |
| Hashtags used | The post itself | "none" is a value |
| First comment used (Y/N) + type | `LinkedIn_Author_First_Comment_System.md` | — |
| Scheduled window (morning/afternoon/evening) | Scheduling System | — |
| Impressions | LinkedIn post analytics | "not provided" |
| Likes / comments / reposts / saves | LinkedIn post analytics | "not provided" |
| Profile views | LinkedIn profile analytics | "not provided" |
| Followers gained | LinkedIn, checked at a fixed point in the day | "not provided" |
| Meaningful conversations (comments replied to, DMs, connection requests sent) | `linkedin_outreach_tracker.xlsx` | "none yet" |

**Numbers are copied exactly, or not written at all.** Never estimate, never reconstruct impressions from likes, never carry yesterday's number forward as a proxy, never present a range as a measurement. "Not provided" is the correct entry when analytics haven't been shared — the standing no-fabrication rule applies to this file exactly as it does to a post.

**Log your own activity separately.** Engagement that came from the author's own first comment or replies is recorded as such, not as audience interest.

---

## Layer 2 — batch review

**Default batch: 9 posts** (~3 days at the current 3/post/day cadence). Extend to **18** only when 9 posts genuinely leave the question open. Never shrink a batch because a trend looks obvious after two posts.

**One variable per batch.** A batch tests exactly one thing — a hook type, a format, a slot ordering, a CTA style, a timezone target, first-comment used vs. not. Everything else stays at the current default. Change two things and a result means nothing about either.

**When a review happens:**

1. **When a batch closes** — after the 9th (or 18th) post's numbers are available. This is a standalone task, not something folded into drafting the next posts.
2. **Immediately, mid-batch, only for a hard failure** — a post LinkedIn rejected, a blocked item that shouldn't have been submitted, a broken link that published. That's a verification failure, not a learning; fix it, log it, keep the batch running.
3. **A 30-day roll-up** — at 90 posts / 10 batches (per `LinkedIn_Master_System.md` Section 52). A roll-up looks for patterns across batches; it does not reinterpret a batch that already closed, and it opens no new variable on its own.
4. **No review on a day nothing published.** There is nothing to learn from an empty day.

---

## Layer 3 — confidence, and what a finding is allowed to do

| Level | What it means | What it's allowed to do |
|---|---|---|
| **LOW** | One post, or a batch where something else also changed | Recorded as an observation. Never cited as a reason to change a default. |
| **MEDIUM** | One clean batch, single variable, no confounders | Recorded and noted. Still not a rule; the next batch on that variable decides. |
| **HIGH** | Same direction across two or more closed batches on the same variable, no plausible alternative explanation | May override a stated preference anywhere in the system (README precedence rule 1). This is the only level that changes a default. |

The exact thresholds behind LOW/MEDIUM/HIGH are **PROPOSED — TBD**, to be revised once real batches exist and it's clear what a "clean signal" looks like at this account's scale. What is not negotiable is the ladder itself: one post can never produce a HIGH-confidence finding.

When a HIGH-confidence finding conflicts with a rule in another file, the finding wins and the other file gets updated or marked superseded — never silently ignored.

---

## What NOT to conclude

- That a post's raw numbers measure its quality. A post can travel far on a hook and still be the weakest thing published that week.
- That a comment count means the right audience arrived. Comments from outside the target audience are worth logging and worth discounting.
- That anything changed when the cadence, timing, topic, and format all moved in the same batch.
- That a post rode the system when it actually rode an external event or a large account's engagement.
- That a percentage difference means anything at small numbers, where a handful of views swings the result.
- That a hypothesis formed *after* seeing the numbers was the hypothesis being tested. It wasn't. It goes in as a new proposed experiment or not at all.

---

## How memory gets updated

| Finding | Memory section that changes |
|---|---|
| A hook type or format performs better/worse | Hook Learnings, Format Learnings |
| A topic or series lands or doesn't | Topic Learnings |
| A pattern to do more or stop doing | Content Patterns To Repeat / To Avoid |
| A timing result | Timing Learnings (baseline schedule changes only at HIGH) |
| A first-comment result | Comment Learnings |
| An open question | Active Experiments / Next Experiments |

**Edit, never recreate.** The memory file is appended to and revised in place. A finding that gets overturned is marked superseded with its date — not deleted, same pattern already used for the 5-post/day → 3-post/day cadence change. A blank section stays the literal string "none yet" until a real finding earns its way in; filling it with assumptions is the failure mode this file exists to prevent.

---

## Required output format

Every closed batch produces this block, alongside the updated memory file:

```
BATCH REVIEW
Batch ID: [Experiment ###]
Variable tested: [exactly one]
Control: [the current default it ran against]
Posts in batch: [n] — published [date range]
Metrics recorded: [yes — from LinkedIn analytics / not provided]
Result: [direction only, with the raw recorded numbers]
Confounding factors: [anything else that changed, or "none identified"]
CONFIDENCE: HIGH / MEDIUM / LOW
DECISION: Adopt as default / Extend to 18 / Abandon — revert to [control] / Record only, inconclusive
MEMORY UPDATED: [section(s) changed, or "none — observation only"]
```

**Current state:** Experiment 001 exists as the first scheduled batch (text-only, per `LinkedIn_Master_System.md` Section 47-48). No analytics recorded yet. Its single variable, batch size, control, and result are **TBD**. No batch has closed, so `LINKEDIN_LEARNING_MEMORY.md` correctly still reads "none yet" in every section.

---

## Core Rule

**MAIN POST:** makes the claim. **ANALYTICS:** test the claim. **THIS FILE:** decides whether the claim was ever true.

The system changes only when real results say so. With no data there is no change. TBD is a valid state for a finding; a guess is not.
