> **DRAFT written by the assistant — review and edit before relying on it.**

# LinkedIn Scheduling System

Companion to every other file. This one governs **when** a post goes out and **what has to be true before it is allowed to**. It does not govern what the post says (`LinkedIn_Operating_System.md`), what hashtags it carries (`LinkedIn_Hashtag_Intelligence_System.md`), whether it passes the final gate (`LinkedIn_Verification_Gate.md`), or whether it worked (`LinkedIn_Self_Learning_System.md`).

---

## 0. Supersession note — read this first

The **3-posts-per-day cadence** (TOFU + MOFU + Authority every day, as morning/afternoon/evening slots) recorded in `LinkedIn_Master_System.md` Section 12 and referenced in `LinkedIn_System_README.md`, `LinkedIn_Verification_Gate.md` and `LinkedIn_Self_Learning_System.md` is **superseded by this file**. Per the project's standing pattern, the old rule is marked superseded, not deleted — it stays as history. Everything below replaces it.

Open items this creates in files not edited here (flag, don't quietly diverge): README's "current cadence (3 posts/day)" line and its Scheduling task flow; Master System Section 12; the Section 52 30-day maths (90 posts at 3/day); Verification Gate's "adequate spacing from the other 2 posts that day"; and Self-Learning's "9-post batch ≈ 3 days" framing (9 posts still stands — it is now ~9 days).

---

## 1. Core rule — one post a day, maximum

- Exactly **one published post per calendar day**, day boundary taken in Asia/Kolkata.
- A post that is never approved **does not count as that day's post**.
- **Never post twice in one day.** Not to catch up after a skipped day, not when a deferred post and today's post are both approved, not when a post is "already written". One publishes; the other moves to the next day. There is no catching-up exception.
- **Skipping a day is compliant.** If there is nothing worth saying, say nothing (Master System Sections 55-56). Posting filler to protect a streak is a breach of the no-fabrication rule, not discipline.
- A skipped day **does not advance the rotation** (see Section 2).

---

## 2. Rotation — TOFU → MOFU → Authority → repeat

- The rotation advances by **published post**, not by calendar day. Next published post takes the next slot.
- **TOFU:** reach/discovery — story, broad insight, contrarian observation. No proof requirement.
- **MOFU:** speaks to the ICP's problems, frustrations, goals and language. No proof requirement.
- **Authority:** proof (case study, real number, before/after, failure with a fix) **when it exists**. Hard evidence is required only if the post makes a claim about results, clients, revenue, performance, cost or metrics. When no real proof exists that day, the slot is filled by a legitimate non-proof type per Master System Section 12 — creator/industry breakdown, technical lesson, pattern analysis, opinion, proposed experiment — never a fabricated number and never a padded metric.
- **No two similar posts in a row.** "Similar" means same slot, same series, same hook type, same format/structure, or the same core topic as the previously published post. If the next post in rotation is similar to the last one, change the slot order, series, hook or format **before** the post is treated as scheduled. Check against the previous published post, and against the last 2-3 once they exist in `LINKEDIN_LEARNING_MEMORY.md`.

---

## 3. Approval-gated publishing (Telegram)

- **Nothing publishes on a timer.** Every post is a draft until Umesh approves it in Telegram.
- The approval request carries: the finished post, the required post output block (Master System Section 47-48), hashtags if any, the first-comment decision (`LinkedIn_Author_First_Comment_System.md`), and the Verification Gate's `POST VERIFICATION` + `FINAL STATUS`.
- Publish **only** on an explicit approval message from Umesh. **Silence is not approval.** No default-publish, no auto-post, no queue that fires without approval. This matches the automation ban in the Author First Comment file and LinkedIn's own guidance on automated posting.
- Telegram is the **approval channel**, not the publisher. Publication is a manual action by Umesh; this system prepares content, it does not post it.
- **Not approved:** the post is held, rewritten, or dropped. It does **not** roll forward on its own, and must pass the Verification Gate again if it is ever revived.
- **Approved after the preferred window closes:** publish that day only if doing so does not create a second post; otherwise it takes the next day's window. An off-window publish is allowed only if Umesh explicitly approves it, and it gets logged as a timing data point.

---

## 4. Preferred windows (Asia/Kolkata)

Every time in this file is **IST**. Windows are preferences, not fixed clock times — the post goes out during the window in which approval arrives, not at a fixed minute.

The old baseline is superseded and does not transfer: the 3-post schedule used roughly 9am / 1pm / 6pm IST with natural day-to-day variation, and carried an explicit note that the variation was **not** for timing-based detection evasion. That note stays true for this schedule too.

**PROPOSED, unconfirmed — these are not facts about the audience:**
- **Morning:** 07:30–09:30 IST
- **Midday:** 12:00–14:00 IST
- **Evening:** 18:30–20:30 IST

**PROPOSED default mapping, also unconfirmed:** TOFU → Morning, MOFU → Midday, Authority → Evening. Treat as a hypothesis, not a finding.

**TBD:** the final window ranges and the default mapping, to be confirmed with Umesh and recorded in this section. Until then, no window here may be cited as a reason a post performed well or badly, and **no claim about "when my audience is active" may be written into this file unless it comes from `LINKEDIN_LEARNING_MEMORY.md`.**

---

## 5. Timing experiments

Per `LinkedIn_Self_Learning_System.md`: one variable at a time, minimum 9 published posts (now ~9 days), confidence recorded in memory. Changing the slot-to-window mapping is a timing experiment and must be named as one in the output block. Publishing a second post on the same day to "test timing" is not an experiment — it is the double-post breach in Section 1.

---

## 6. Required output format

Every post sent to Telegram for approval carries this block:

```
SCHEDULED POST
Date (IST):
Slot: TOFU / MOFU / Authority
Series:
Preferred window (IST): Morning / Midday / Evening
Approval: PENDING — explicit approval required in Telegram
Publish trigger: author approval message (not a timer)
Previous published post: [slot + series + hook type]
Why this is not similar to the previous post:
If not approved: held / rewritten / dropped — no auto-roll-forward
If approved after the window closes: [next day's window / approved off-window]
Timing experiment this post belongs to: [name, or "none"]
```

There is no multi-post batch block any more. At one post a day, the unit is the single block above, re-checked against `LINKEDIN_LEARNING_MEMORY.md` each time a 9-post experiment closes.

---

## 7. What this file does not govern

- Post content, series, hook type — `LinkedIn_Operating_System.md`
- Hashtags — `LinkedIn_Hashtag_Intelligence_System.md`, and only after the content is final
- The pass/fail gate and live re-verification — `LinkedIn_Verification_Gate.md`
- Whether the post actually worked — `LinkedIn_Self_Learning_System.md` + memory file

Timing questions never open the Comment Intelligence or Creator Research docs.

---

## 8. What to update, and when

| After this happens | Update |
|---|---|
| A timing experiment closes | `LINKEDIN_LEARNING_MEMORY.md` (the finding) |
| Umesh confirms a window range or the slot→window mapping | this file (Section 4) — replace TBD, nothing else |
| The cadence changes again | this file + `LinkedIn_Master_System.md` Section 12, marking the old version superseded, never deleting it |

---

## The rule that overrides this one

If a post is ready and not approved, there is no schedule — there is a draft and a waiting approval. And never invent a metric, quote, creator, follower count or personal experience to justify a timing decision: **"could not verify" or "TBD" beats a plausible-sounding guess.**
