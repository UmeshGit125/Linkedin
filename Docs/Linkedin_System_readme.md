# LinkedIn System — README (read this file first, always)

This is the entry point. Any AI session working on this LinkedIn project — including a future one with no memory of how this was built — should read this file before touching any other file in `linkedin-data`. It says what each file is for, what order to read them in for a given task, and which files to skip so context isn't wasted on rules that don't apply to the task at hand.

---

## The files, one line each

| File | What it actually contains | Type |
|---|---|---|
| `LinkedIn_System_README.md` | This file. Routing/index only — no content rules live here. | Meta |
| `LinkedIn_Master_System.md` | Top-level index: profile/positioning (Section 1), current cadence (3 posts/day), and a map of which section of the original spec lives in which file. Read this second. | Index |
| `LinkedIn_Operating_System.md` | The actual content rules: four core ideas (Reviewable Automation, Confidence-Based Routing, Honest Scoping, No Padded Metrics), the seven content series, the Proof Inventory field list, confidentiality tiers (1-4), the hook system, banned hooks, the 70/20/10 mix. Has one superseded section (old weekly cadence) — marked, not deleted. | Rules |
| `LinkedIn_Comment_Intelligence_System.md` | Where and how to comment on other people's posts: four creator categories (Top/ICP/Peer/Adjacent), the 8-axis post-scoring system, comment angles, human-writing rules, per-post-type playbook, required output format. | Rules |
| `LinkedIn_Hashtag_Intelligence_System.md` | Hashtag selection only: topic-first process, 0-3 default, quality test, placement, funnel-stage mapping, required output format. | Rules |
| `LinkedIn_Self_Learning_System.md` | How to test anything (hooks, formats, cadence itself) against real results instead of assumption: batch/experiment discipline, 9-post default sample size, confidence levels, what NOT to conclude from one post. | Rules |
| `LinkedIn_Scheduling_System.md` | WHEN each of the 3 daily posts goes out: morning/afternoon/evening time windows per slot, natural day-to-day variation within those windows (not fixed clock times, and explicitly not timing-based detection evasion), timing-experiment rules, and the required per-batch scheduling output format. | Rules |
| `LinkedIn_Verification_Gate.md` | The final pre-schedule/pre-publish gate: conditional checklist (Content/Proof/Visual/Hashtags/CTA/Links/Tags/First comment/Format/Schedule/Strategy) run against one specific post, required `POST VERIFICATION` + `FINAL STATUS` output, and a post-schedule re-verification step against the live platform (never trust memory). | Rules |
| `LinkedIn_Author_First_Comment_System.md` | The ONE planned author comment on the author's OWN post after publishing (different from Comment Intelligence, which is about commenting on others' posts): when a first comment adds genuine value vs. N/A, content rules (extend, don't summarize, no engagement bait), human-writing rules, and its own Pre-Publish Check — folded into the Verification Gate as a conditional item. | Rules |
| `LINKEDIN_LEARNING_MEMORY.md` | The living scoreboard. Updated after every real batch — never recreated. Currently a template; every section says "none yet" because nothing has published under this system yet. | Live data |
| `LinkedIn_Creator_Research.md` | Verified research on ~16 real creators (Tier 1 direct-niche, Tier 2 LinkedIn-growth, Tier 3 from your source material), each with a source-traceability block and confidence rating. | Research |
| `linkedin_content_system.xlsx` | Three working sheets: **Proof Inventory** (real project data — mostly TBD on numbers, real on architecture/decisions), **Content Database** (post log), **Target Accounts** (creator/account targets by category). | Live data |
| `linkedin_outreach_tracker.xlsx` | Real log of comments posted and connection requests sent, with follow-up-timing formulas. | Live data |
| `reviewable_automation_diagram.png` | One hand-built diagram (confidence-routing architecture), made for a specific draft post. | Asset |

---

## Precedence — what wins when two files seem to disagree

1. **`LINKEDIN_LEARNING_MEMORY.md` beats every assumption once it has real data.** A confirmed learning there (HIGH confidence) overrides a stated preference anywhere else, including this README.
2. **`LinkedIn_Master_System.md` beats `LinkedIn_Operating_System.md` on cadence specifically.** The Operating System doc's old weekly-cadence section is marked superseded — don't follow it, it's kept for history only.
3. Everywhere else, the more specific file wins over the more general one (e.g. for a hashtag question, the Hashtag doc beats a passing mention of hashtags anywhere else).
4. Nothing overrides the standing no-fabrication rule: never invent a metric, quote, client result, or personal experience, in any file, ever. If a real number doesn't exist yet, say TBD or "could not verify" — this rule has no exceptions and no file can override it.

---

## Read order by task

**Writing a new post (any of the 3 daily slots — TOFU / MOFU / Authority-BOFU-Breakdown):**
1. `LinkedIn_Master_System.md` Section 1 (positioning) + current cadence
2. `LinkedIn_Operating_System.md` (which series, which hook type, confidentiality tier for the project being referenced)
3. `linkedin_content_system.xlsx` Proof Inventory sheet — pull the real fields, leave TBD fields out rather than inventing them
4. `LINKEDIN_LEARNING_MEMORY.md` — check Hook/Topic/Format Learnings and Content Patterns To Avoid/Repeat before finalizing
5. `LinkedIn_Author_First_Comment_System.md` — decide First comment = Prepared or N/A before the post is considered done
6. `LinkedIn_Verification_Gate.md` — run before scheduling/publishing, not before
7. Skip: Comment Intelligence doc, Creator Research doc (unless the post is specifically a creator breakdown, see below)

**Scheduling a batch (deciding WHEN the 3 posts go out, not what they say):**
1. `LinkedIn_Scheduling_System.md` — full read, it's the only file that governs timing
2. `LINKEDIN_LEARNING_MEMORY.md` — check for any confirmed/probable timing learnings before defaulting to the 9am/1pm/6pm baseline
3. Produces the required scheduling output block (POST 1/2/3 + Batch Experiment) alongside the actual post content from the flow above
4. Skip: Hashtag doc, Comment Intelligence doc — timing has nothing to do with either

**Post is specifically a creator/industry breakdown:**
1. `LinkedIn_Creator_Research.md` for the verified facts about that creator
2. `LinkedIn_Operating_System.md` Creator Breakdown Rule (source of insight, never source of wording)
3. Then the "writing a new post" order above

**Deciding whether/what to comment on someone else's post:**
1. `LinkedIn_Comment_Intelligence_System.md` — full read, it's the only file that governs this
2. `LinkedIn_Creator_Research.md` if the target is one of the already-researched creators
3. `linkedin_outreach_tracker.xlsx` — check if this person/post is already logged before commenting again
4. Skip: Hashtag doc (hashtags don't apply to comments), Self-Learning doc (comment performance isn't part of the post-batch experiment loop unless you're specifically tracking comment-to-DM conversion)

**Choosing hashtags for a finished post:**
1. `LinkedIn_Hashtag_Intelligence_System.md` only — the post's topic must already be decided before opening this file
2. Skip everything else; this is a narrow, final step

**Running or reviewing a batch experiment:**
1. `LINKEDIN_LEARNING_MEMORY.md` — read current state first, always
2. `LinkedIn_Self_Learning_System.md` — the method (batch size, one-variable-at-a-time, confidence levels)
3. `linkedin_content_system.xlsx` Content Database sheet — the actual per-post metrics if analytics were provided
4. Update `LINKEDIN_LEARNING_MEMORY.md` at the end — this is the only file that should change as a result of this task, besides the xlsx log

**Researching a new creator (expanding the Creator Research doc, or Comment Intelligence's Category A-D targets):**
1. `LinkedIn_Creator_Research.md` — see its Section 0 methodology (confidence levels, "could not verify" discipline) before adding anyone
2. `LinkedIn_Comment_Intelligence_System.md` Section 21 — the four-category structure to slot them into
3. Do real research (search/fetch) — never fill in a creator from memory or pattern-match to "creators like this usually have X followers"

**Filling in real Proof Inventory data (when Umesh provides a real number):**
1. `linkedin_content_system.xlsx` Proof Inventory sheet — replace the specific TBD cell, nothing else
2. No other file needs to change unless the new data unlocks a post type that was previously blocked (e.g. a Series 02 "AI Failed Here" post becomes possible once a real Failure/Root cause/Fix is filled in)

**A brand-new AI session with zero memory of this project (cold start):**
1. This README, in full
2. `LinkedIn_Master_System.md`, in full
3. `LINKEDIN_LEARNING_MEMORY.md`, in full (it's short until real data exists)
4. Then only the specific rule file(s) the actual task needs, per the task list above — reading all seven files for every single task wastes context and isn't necessary

---

## What to update, and when

| After this happens | Update this file |
|---|---|
| A batch of real posts publishes and analytics come in | `LINKEDIN_LEARNING_MEMORY.md` (required) + `linkedin_content_system.xlsx` Content Database (per-post row) |
| A comment gets posted on someone's LinkedIn post | `linkedin_outreach_tracker.xlsx` |
| Umesh provides a real number for a TBD field | `linkedin_content_system.xlsx` Proof Inventory sheet only |
| A timing pattern gets enough evidence to matter | `LINKEDIN_LEARNING_MEMORY.md` (the finding) — `LinkedIn_Scheduling_System.md` only changes if the baseline schedule itself needs revising |
| A new creator gets researched | `LinkedIn_Creator_Research.md` (add with full source-traceability block, never estimate) |
| The cadence or a core rule changes again | `LinkedIn_Master_System.md` Section 12 (or the relevant section) — mark the old version superseded, don't delete it, same pattern already used for the 5-post/day → 3-post/day change |

---

## The one rule that overrides everything above

If a task doesn't clearly map to one of the flows above, don't guess which file matters — check `LinkedIn_Master_System.md`'s index first, and if it's still unclear, ask rather than assume. And regardless of which file is open: never invent a metric, quote, creator, client result, or personal experience. "Could not verify" or "TBD" beats a plausible-sounding guess every time.