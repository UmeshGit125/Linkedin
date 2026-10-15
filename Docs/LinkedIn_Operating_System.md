> **DRAFT written by the assistant — review and edit before relying on it.**

# LinkedIn Operating System

Companion to `LinkedIn_Master_System.md` (the index) and `LinkedIn_System_README.md` (the entry point). The master says what exists; this file holds the day-to-day content rules: core ideas, series, Proof Inventory, confidentiality tiers, hooks, banned phrasing, the 70/20/10 mix, the 3-post structure, the daily loop, and Section 34 (visuals).

Section numbers are the shared project numbering, so cross-references from other files — e.g. `LinkedIn_Verification_Gate.md` citing "Section 34B" — land in the right place. Sections 1–23 and 38–56 belong to other files; this file carries 24–37.

---

## 24. The four core ideas

Not topics — the point of view every series, hook and comment is downstream of.

- **Reviewable Automation** — automation that surfaces its own decisions instead of acting unobserved. In a post: what the review step catches, not how clever the model is.
- **Confidence-Based Routing** — confident work runs automatically; low-confidence items go to an exception queue for a human. This is the architecture of the `reviewable_automation_diagram.png` asset. In a post: the routing rule and its cut-off.
- **Honest Scoping** — say exactly what was built and where it stops. Umesh is a student and an intern; nothing gets described as more than that. Name the limitation before someone else does.
- **No Padded Metrics** — a number that doesn't exist stays TBD. A missing metric is a reason to rewrite the post, never to round, estimate, or approximate.

## 25. The seven content series

| Series | What it covers | Proof needed |
|---|---|---|
| 01 Production AI | How an AI system actually enters a working workflow: services, APIs, auth, error paths, evaluation. | No — but must be true of real work. |
| 02 AI Failed Here | One real failure, its root cause, the fix. | Yes — needs a real Failure/root cause/fix row. TBD today, so this series is blocked until one is filled. |
| 03 What AI Actually Cost | The honest cost of building and running a system. | Yes — real numbers, currently TBD. |
| 04 Things I Refused to Automate | Steps deliberately kept manual, and why. | No — must cite a real decision. |
| 05 Shipping AI Across Borders | What changes when one system crosses environments (local → cloud, GCP/AWS S3, Docker). | No — exact intended angle TBD, confirm. |
| 06 AI Project Autopsy | A finished project taken apart: intent, what got built, what held, what broke. | Yes — real project, real detail, no invented post-mortem. |
| 07 Things Nobody Put in the Demo | The unglamorous parts of a working system that never make the demo. Humour only from real engineering experience. | No. |

Any series can fill any slot in Section 33.

## 26. The 70/20/10 mix

The mix is 70/20/10 across three content categories that are **TBD** — not recorded in this system's sources, so confirm with Umesh before using the ratio to plan a batch. Two parts are firm: the mix is a target, not a quota, and it never justifies a post with no real material behind it.

## 27. Proof Inventory — the required fields

Source: `linkedin_content_system.xlsx`, Proof Inventory sheet.

| Field | Status today |
|---|---|
| Project + one-line purpose | Real (from the resume) |
| Stack | Real |
| Key architecture and decisions | Real |
| What was deliberately not automated | Real |
| Failure → root cause → fix | TBD for most projects |
| Real metric (accuracy, latency, cost, users, time saved, before/after) | TBD — none exist yet |
| Asset (real screenshot/diagram) | Partly real |
| Confidentiality tier (1–4) | Must be set before the asset or number is used |
| Verification status | Set only when Umesh confirms |

A post may reference a filled field only. TBD fields are left out of the post, not estimated.

## 28. Confidentiality tiers (1–4)

Hard rule: no confidential detail of PW LeapX internal work beyond what is on the resume. Souli's counselling data and CallAudit's call transcripts are examples of material that never becomes content. Tier definitions below are **PROPOSED** — confirm before use.

- **Tier 4 — Public:** resume-level facts (project name, stack, one-line description, public architecture). May be named directly.
- **Tier 3 — Public-safe detail:** implementation detail, a diagram or screenshot Umesh made, with internal identifiers redacted. May appear once redacted.
- **Tier 2 — Internal:** employer process, code, prompts, internal numbers, transcripts. Described only in general terms, never quoted or shown.
- **Tier 1 — Restricted:** client or customer data, personal data (counselling content, call recordings and transcripts), anything under an NDA. Never appears in a post, comment, first comment or visual, in any form.

If the tier is unclear, treat it as Tier 1.

## 29. The hook system

The hook is the first line, and the only line that has to earn the read.

- It must be literally true of the post: no promise the post doesn't keep, no result the Proof Inventory doesn't hold, no "I built X" for a plan.
- Hooks come from the material — a real number, constraint, failure, decision or observation — not a template.
- Vary the shape between consecutive posts; the same structure three posts running is a repeat even if the words change.
- Enumerated hook types are **TBD** — don't treat any list as complete until confirmed.
- Hook performance is tested, logged in `LINKEDIN_LEARNING_MEMORY.md`, never assumed from one post.

## 30. Banned hooks

Never used, in any series: a hook whose number isn't in the Proof Inventory; any first-person claim of experience Umesh doesn't have (client work, revenue, a team, "we scaled"); engagement bait ("Thoughts?", "Agree?", "Anyone else?"); another creator's hook reworded; manufactured stakes or a cliffhanger the post doesn't pay off.

## 31. Human writing rules

Applies to posts, first comments, and comments on others' posts. Never lean on: "One thing worth noting…", "The interesting part…", "The key takeaway…", "Here's the thing…", "This is important because…", "I'd rather…", "Most people…". The same opening structure on consecutive posts counts as a repeat even if the wording differs. If a draft could have been written about any AI project, it isn't specific enough to post.

## 32. Evidence-only rules

- Real experience only — nothing that happened to someone else gets told as Umesh's.
- Real case studies only — a project enters a post once it's in the Proof Inventory with a tier set.
- Hypotheticals are allowed only when labelled hypothetical in the post itself.
- **Creator breakdown rule:** creator content is a source of insight, never of wording. Cite the creator, take the idea, write the analysis in Umesh's own words. Creator facts come from `LinkedIn_Creator_Research.md` or fresh research, never memory.
- If a source can't be verified, it doesn't appear as fact.

## 33. The 3-post daily structure

Three posts a day, every day. The cadence's measurement discipline lives in `LinkedIn_Self_Learning_System.md`.

1. **TOFU** — reach and discovery: story, broad insight, strong observation, contrarian idea. No proof requirement.
2. **MOFU** — the ICP's problems, frustrations, goals and language, directly. No proof requirement.
3. **Authority / Creator breakdown / BOFU / Experiment** — real proof when it exists (case study, experiment, number, before/after, failure with fix); otherwise a legitimate non-proof type (opinion, pattern analysis, creator/industry breakdown, technical lesson, observation, proposed experiment).

The proof rule governs claims, not the slot. Evidence is required only for a claim about results, clients, revenue, growth, performance, cost, before/after or a metric. **REAL DATA > MORE CONTENT. TRUST > POSTING FREQUENCY.**

**Superseded (kept for history, do not follow):** the earlier weekly cadence (3x/week plus a lighter daily post) and the brief 5-posts/day experiment.

## 34. Visuals

**34A — Default: text-only is a valid finished state.** TOFU and MOFU posts — stories, observations, opinions, lessons — go out as text. No image is required, and none is added just so the post has one. Visual = N/A in the Verification Gate.

**34B — When a real image is required.** Authority, proof, result, system and breakdown posts — anything whose point is evidence — carry a real image: a real screenshot of the actual thing, a real diagram Umesh built (e.g. `reviewable_automation_diagram.png`), or a real photo. Rules:

- The image must be the thing the post is about; a stand-in graphic of "an AI system" is not a screenshot.
- Tier set and redaction applied before use, per Section 28. Tier 1 never appears; Tier 2 only as a general description, never the artifact.
- No fake dashboards, invented UI, or made-up results.
- No AI-generated image is presented as a real screenshot, result, or real system output.

**AI-generated illustrations — the one carve-out.** On non-proof posts only (TOFU, MOFU, story, opinion), an AI-generated illustration is allowed if it contains **no text and no data** — no numbers, labels, charts or fake UI. It is decoration, never evidence, and is never captioned as the real system. Anything outside that box is banned.

Assets are attached before the Verification Gate runs, so "Visual: ✅/N/A/❌" is checked honestly. Asset storage location: TBD.

## 35. The daily operating loop

Draft → gate → Telegram approval → publish. Nothing skips a step.

1. **Draft** — work the read order in the README (positioning + cadence → this file → Proof Inventory → `LINKEDIN_LEARNING_MEMORY.md`), then produce the three posts in the Section 36 format. Real fields only.
2. **Gate** — `LinkedIn_Verification_Gate.md` runs against each post individually. 🔴 BLOCKED doesn't leave this step. The first-comment decision (Prepared / N/A — Not needed) is made here.
3. **Telegram approval** — gated drafts go to Umesh on Telegram with status, slot and TBD flags. He approves, edits or drops each one. **No post publishes without explicit approval.** Bot/channel details: TBD.
4. **Publish** — manual, in the window set by `LinkedIn_Scheduling_System.md`; first comment posted manually if prepared; then the live post is re-verified against the draft. No automation publishes, likes, comments or posts the first comment.
5. **Log** — Content Database rows, `linkedin_outreach_tracker.xlsx` for comments, learnings in `LINKEDIN_LEARNING_MEMORY.md`. Nothing is concluded from one post.

## 36. Post output format

```
POST TYPE / TOPIC / HOOK / POST / HASHTAGS / FIRST COMMENT
WHY THIS WORKS / SOURCE-INSPIRATION / ORIGINALITY / CONFIDENCE
```

Spec: `LinkedIn_Master_System.md` Sections 47–48. Hashtags are chosen last, after the post is finished, per the Hashtag Intelligence doc (default 0–3, topic-first).

## 37. What is not in this file

Comments on others' posts → `LinkedIn_Comment_Intelligence_System.md`. Hashtags → `LinkedIn_Hashtag_Intelligence_System.md`. Timing → `LinkedIn_Scheduling_System.md`. Testing → `LinkedIn_Self_Learning_System.md`. Checklist → `LinkedIn_Verification_Gate.md`. First comment → `LinkedIn_Author_First_Comment_System.md`. Anything unmapped → check the master's index, then ask rather than assume.

**Core rule:** real data over more content, real experience over fake stories. If a slot has nothing real to say, it takes a form that needs no proof — or it doesn't go out.
