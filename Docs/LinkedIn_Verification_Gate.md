# LinkedIn Pre/Post-Schedule Verification Gate

Companion to every other file — this is the final gate a post passes through immediately before scheduling/publishing, and the check run again against what actually got scheduled. Not a new strategy, a checklist that applies the existing rules (Operating System, Hashtag Intelligence, Scheduling System, Self-Learning System) conditionally to one specific post.

**Hard rule:** if any requirement that actually applies to a post is missing, the status is 🔴 BLOCKED. Never output 🟢 READY when an applicable requirement is unmet — and never invent a requirement that doesn't apply to this post type just to have more boxes to check.

---

## Step 1 — identify what applies to this specific post

Before checking anything, determine: content type/series, purpose, format, whether it makes a proof/evidence claim, whether a visual is required or included, whether hashtags are required, whether a CTA/link/tag is intended, and the scheduling slot/window it's meant for. Everything below is conditional on this — most posts will have several genuine "N/A" rows, and that's correct, not a shortcut.

## Step 2 — the checklist

**Content (always applicable):** correct post type for the slot it's filling; clear purpose; clear idea; original (passes the Creator Breakdown Rule if creator-sourced); useful; relevant to the ICP; no fabrication; no unsupported claims; no copied creator wording; human-writing rules followed (no banned-phrase repetition, varied structure vs. recent posts); not excessively repetitive with recent posts (checked against `LINKEDIN_LEARNING_MEMORY.md` and the last 2-3 relevant posts).

**Proof (conditional):** applies only if the post contains numbers, metrics, results, a case study, a client claim, a cost, a before/after, or any evidence-based claim. If so: evidence exists in `linkedin_content_system.xlsx` Proof Inventory or another trusted source; the claim matches that evidence exactly; no estimate is presented as fact; nothing fabricated. If the post makes no such claim: **Proof = N/A**, not blocked.

**Visual (conditional):** applies only if a visual is included, or the post's type requires one per the Operating System's Section 34B (Authority/Proof/Breakdown posts — real image required; TOFU/MOFU opinion posts — text-only is a valid default, not a gap). If required: the visual exists, is the correct/relevant one, meets the real-not-AI-generated rule, confidential details are redacted per the confidentiality tiers, and it isn't presented as something it isn't. If not required: **Visual = N/A** — never block a TOFU/opinion post for lacking one.

**Hashtags (conditional):** per `LinkedIn_Hashtag_Intelligence_System.md` — default 0-3, topic-first, never decided before the content. If a specific number or set was explicitly required for this post, verify it's present and correct; if hashtags are simply optional here, **Hashtags = optional**, not mandatory.

**CTA (conditional):** only required if the post's purpose genuinely calls for one. Never force "What do you think?" by default — **CTA = N/A** is a valid, common outcome.

**Link / Tag-mention (conditional):** only applicable if a link or a person/company tag was actually intended for this post. Otherwise **N/A**.

**First comment (conditional, per `LinkedIn_Author_First_Comment_System.md`):** applies to every post — the decision itself is never optional, even though the comment is. Determine whether a genuine additional point exists (context, caveat, example, implementation detail, left-out clarification, or a real follow-up question — never a summary of the post, never generic engagement bait like "Thoughts?"). If yes: exactly one comment prepared, checked against that file's Pre-Publish Check (adds new information, doesn't repeat the post, relevant, human, no fabricated claims, not engagement bait, not copied from another creator). If no genuine addition exists: **First comment = N/A — Not needed**, which is a valid, common outcome, not a gap. Never force one just to fill the slot. The comment itself is posted manually by Umesh after publish — this gate verifies it's prepared and passes the checklist, not that it's been posted.

**Format:** correct structure for this post's type; no prohibited formatting (banned hooks list, hashtag stuffing, forced list-of-3 template); readable.

**Scheduling:** correct post assigned to the correct daily slot; correct date/time/timezone; matches the timezone-target experiment currently running (see `LINKEDIN_LEARNING_MEMORY.md` Active Experiments); adequate spacing from the other 2 posts that day; doesn't contradict `LinkedIn_Scheduling_System.md`.

**Strategy alignment:** supports the primary goal (followers + meaningful connections + relevant audience + authority — not impressions/likes/virality); fits the current 3-post structure; fits the current experiment; doesn't contradict any file in the system; doesn't add complexity with no execution value.

## Step 3 — required output format

```
REQUIRED & VERIFIED
- [list every mandatory item that applies, each marked verified]

NOT APPLICABLE
- [list every item that doesn't apply to this post, so it's clear it was considered, not skipped]

POST VERIFICATION
Content: ✅ / ❌
Proof: ✅ / N/A / ❌
Visual: ✅ / N/A / ❌
Hashtags: ✅ / N/A / ❌
CTA: ✅ / N/A / ❌
Links: ✅ / N/A / ❌
Tags: ✅ / N/A / ❌
First comment: ✅ Prepared / N/A — Not needed / ❌
Format: ✅ / ❌
Schedule: ✅ / ❌
Strategy: ✅ / ❌

FINAL STATUS
🟢 READY TO SCHEDULE/PUBLISH
or
🔴 BLOCKED — [specific reason, and whether it's fixable now or needs to wait on Umesh]
```

## Step 4 — after scheduling, re-verify the live version

Don't treat the task as done because LinkedIn accepted the click. Go back and check the actual scheduled post (LinkedIn's "View scheduled posts") for: correct text, correct visual if applicable, correct hashtags if applicable, correct CTA if applicable, correct date/time/timezone. A UI glitch, an autocorrect, or a misclick during scheduling is a real failure mode this step catches.