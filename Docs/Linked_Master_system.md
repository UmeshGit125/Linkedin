# Master LinkedIn Growth, Creator Research & Content Intelligence System

This is the top-level, consolidated version of everything built so far. Section 1 is filled in from what's already established in this project; Sections 2-56 are your spec, kept verbatim in structure. The full system is now made up of:
- `LinkedIn_Operating_System.md` — positioning, four core ideas, six content series, Proof Inventory, confidentiality tiers, hook system, banned hooks, 70/20/10 mix
- `LinkedIn_Comment_Intelligence_System.md` — commenting on OTHER people's posts: targeting, scoring, writing rules
- `LinkedIn_Hashtag_Intelligence_System.md` — hashtag selection process and rules
- `LinkedIn_Self_Learning_System.md` — the batch/experiment/measurement discipline (Part 57): how cadence, hooks, formats, and every other variable get tested against real results instead of assumed
- `LinkedIn_Scheduling_System.md` — when each of the 3 daily posts goes out (morning/afternoon/evening time windows with natural day-to-day variation, not fixed clock times), the timing-experiment rules, and the required per-batch scheduling output
- `LinkedIn_Verification_Gate.md` — the final pre-schedule/pre-publish checklist run against one specific post, plus the post-schedule re-verification step against the live platform
- `LinkedIn_Author_First_Comment_System.md` — the ONE planned author comment on the author's OWN post after it publishes (not commenting on others' posts — that's the Comment Intelligence file above)
- `LINKEDIN_LEARNING_MEMORY.md` — the living memory file the self-learning system reads and updates every batch; currently a template since no posts have published with tracked analytics yet

This master file is the index and the single source of truth for anything that isn't already detailed in one of those files. `LinkedIn_System_README.md` is the top-level entry point — read that first for which file to open for a given task.

---

## 1. Profile and positioning (rebuilt from Umesh's resume, 2026-10-10)

Every fact below comes from the resume (`resume.pdf`). Items marked **PROPOSED** are reasonable defaults, not facts — confirm or change them. The earlier version of this section described a different person (Suraj Yadav) and was replaced in full; nothing from it applies to Umesh.

- **Name:** Umesh Sharma
- **Role:** AI/ML Intern at PW LeapX (Bangalore, Dec 2025 – present); Data Science & AI undergraduate
- **Education:** B.S. (Honours) in Data Science & Artificial Intelligence, IIT Madras (2024 – 2028); UG in Computer Science, PW Institute of Innovation (2023 – 2027)
- **What I'm building (real work only):**
  - At PW LeapX: LLM-powered applications, end-to-end ML pipelines, FastAPI backend services (modular architecture, REST APIs, auth), NLP and automation use cases in production workflows
  - **Souli** — voice-based inner-wellness companion: multi-phase state machine for dialogue, RAG over counseling data (Qdrant + sentence-transformers), embedding-based classification of user input into emotional states, Whisper speech-to-text + LLM responses (Ollama)
  - **CallAudit** — LLM-based call quality auditing from transcripts (FastAPI, Azure OpenAI, PostgreSQL), structured quality insights, role-based evaluation perspectives
  - **AI email assistant** (n8n + GPT-4.1-mini): classification, sender extraction, semantic categorisation, conditional personalised replies
  - **AI personal assistant with LLM agents** (n8n + Groq LLaMA 4): multi-step task automation with structured tool-calling, deterministic execution logic to reduce ambiguity
- **Skills:** Python, SQL, C (basic); regression, classification, supervised/unsupervised learning; RAG, prompt engineering, LLM integration; NumPy, Pandas, scikit-learn, NLTK, Matplotlib, Seaborn; FastAPI, Streamlit, n8n, Docker, Git; GCP, AWS S3; PostgreSQL
- **Certifications:** Machine Learning Bootcamp (Udemy), SQL Certification (Simplilearn)
- **Industry:** Applied AI / GenAI engineering
- **Geography:** Bangalore, India
- **Target audience — PROPOSED:** hiring managers, founders and engineers at AI startups and product companies (India + remote) who hire applied-AI interns and junior engineers; secondarily, other students and early-career builders learning applied AI
- **LinkedIn goal — PROPOSED:** land an Applied AI / GenAI internship or full-time role, and build visibility as a hands-on builder; follower growth is a side effect, not the goal
- **Topics to own — PROPOSED (each backed by real work above):**
  1. Building RAG systems that actually retrieve the right thing (Souli)
  2. Voice AI in practice — Whisper + state machines + LLMs (Souli)
  3. Using LLMs to evaluate conversations (CallAudit)
  4. Making LLM agents reliable — tool-calling and deterministic logic (n8n assistants)
  5. Learning applied AI while studying and interning (IITM BS + PW LeapX)
- **Current followers:** TBD — check the real profile; never state a number without checking
- **Topics not to discuss:** TBD — open item. Default: no confidential details of PW LeapX internal work beyond what's on the resume
- **Creators currently followed:** TBD — open item
- **Existing content / proof:** the four projects above (resume-level detail only). **No metrics exist yet** — any post claiming numbers (accuracy, latency, users, cost, time saved) needs a real number from Umesh first

Positioning constraint: do not sound like a generic AI expert, guru, founder or motivational speaker, and never overstate experience — Umesh is a student and intern. The distinct point of view is a hands-on builder showing what really happens when you build LLM systems: what worked, what broke, what he learned.

---

## 2-11. Research, sourcing, creator discovery, reverse-engineering, gap-finding, YouTube research, comment mining

These sections describe the research discipline already in active use across this project:
- Real research only, "Could not verify" instead of guessing (applied in `LinkedIn_Creator_Research.md`)
- Source priority: LinkedIn > YouTube > X > podcast > newsletter > website > secondary source
- VERIFIED FACT / ANALYSIS / INFERENCE / OPPORTUNITY separated, with a CONFIDENCE level (applied throughout the Creator Research doc's reformatted version)
- Creator scorecard and Top 20 list, source traceability blocks (CREATOR / ORIGINAL SOURCE / DATE / VERIFIED METRICS / TOPIC / UNDERLYING IDEA / WHY IT WORKED / MY ORIGINAL ANGLE) — same template now standard for any new creator research
- Content gap mapping — the Tier 1/Tier 2 gap already identified (production-AI practitioners vs. LinkedIn-growth creators rarely overlapping) is the flagship finding so far
- YouTube-specific and comment-mining research — **not yet done**. Open task: these require the same fetch-and-verify discipline as the LinkedIn/X research already completed, and haven't been run yet. Flagging rather than filling with assumptions.

---

## 12. The daily content funnel — RESOLVED, updated again, this is now the active cadence

**Current decision (supersedes the 5-posts/day rule that briefly replaced the "3x/week + daily lighter" cadence — cadence has now settled at 3/day):** 3 posts per day, every day. Full testing/measurement discipline for this cadence lives in `LinkedIn_Self_Learning_System.md`; this section just states the structure.

**Daily 3-slot structure:**
1. **TOFU** — reach/discovery: story, broad insight, strong observation, contrarian idea, founder lesson. No proof requirement.
2. **MOFU** — speaks to the ICP's problems/frustrations/goals/language directly. No proof requirement.
3. **Authority / Creator Breakdown / BOFU / Experiment** — real proof (case study, experiment, number, before/after, failure with fix) **when available**; otherwise a non-proof substitute (opinion, pattern analysis, creator/industry breakdown per the Creator Breakdown Rule in Section 13, technical lesson, personal observation, proposed experiment, industry insight). This is the only slot the proof rule governs — it is not automatically a "make something up" slot on days without real material.

**The proof rule, unchanged in substance, just applied to 3 slots instead of 5:**
- Hard, verifiable evidence is required **only** when a post makes a claim about results, clients, revenue, growth, performance, cost, before/after numbers, or metrics.
- When it doesn't exist for that day, don't manufacture it — use a legitimate non-proof content type instead.
- Priority: **REAL DATA > MORE CONTENT. TRUST > POSTING FREQUENCY.**

Default experiment size for testing anything (hooks, formats, hashtags, CTAs): **9 posts** (~3 days at this cadence), extendable to 18 if 9 isn't enough evidence. See `LinkedIn_Self_Learning_System.md` for the full batch/measurement/memory-update discipline — nothing here is applied on faith; it's a hypothesis until real analytics from `LINKEDIN_LEARNING_MEMORY.md` say otherwise.

The Operating System doc's Series 01-07 aren't tied to specific weekdays — any series can fill any TOFU/MOFU/Authority slot depending on whether it needs proof that day.

---

## 13-22. Creator breakdown rule, originality, human writing, AI pattern detection, real-experience-only, real-case-studies-only

All consistent with, and now folded into, the existing docs:
- Creator content is source of insight, never source of wording — same rule as the Comment Intelligence doc's "Creator Breakdown Rule"
- No fake personal experience, no fake case studies, hypothetical examples explicitly labeled — same as the Operating System's evidence-only firewall and Part 18's rules already applied to the 10 sample posts
- Human writing / AI pattern detection / banned generic phrases — same list already governing both post-writing (Part 19) and comments (`LinkedIn_Comment_Intelligence_System.md` Sections 25-26), now applying account-wide

---

## 23-31. Comment intelligence

Fully covered by `LinkedIn_Comment_Intelligence_System.md` — that file is the detailed reference; this master doc just confirms it's still the authority for anything comment-related.

---

## 32-35. Hashtag intelligence

Fully covered by `LinkedIn_Hashtag_Intelligence_System.md` — same relationship as above.

---

## 36-37. Content ideas at scale + scoring

Your spec asks for 30 TOFU + 30 MOFU + 20 BOFU + 20 creator breakdowns + 20 personal stories + 20 contrarian + 20 data/experiment + 20 industry insight ideas — 180 ideas, scored on 10 axes each.

Not generated yet, and I don't want to bulk-generate 180 ideas the way the earlier "10 sample posts" round already showed is the wrong instinct: most of those buckets (BOFU, data/experiment, personal stories) depend on real Proof Inventory data that's mostly still TBD. Generating 180 ideas today would mean either padding with generic non-evidence ideas (fine for TOFU/contrarian/industry-insight, not fine for BOFU/data/personal-story) or quietly fabricating specifics to hit the count. Better to size this to what the real data can actually support — see the question below.

---

## 38-46. Writing rules, humor, CTA variety, positioning, series, anti-repetition, content diversity, real-data-vs-analysis, source traceability

All already in force:
- Series in active use: Production AI, AI Failed Here, What AI Actually Cost, Things I Refused to Automate, Shipping AI Across Borders, AI Project Autopsy, Things Nobody Put in the Demo (Series 01-07 in the Operating System doc)
- Humor only from real engineering experience, never manufactured (already the rule in Series 07)
- CTA variety, varied structure/length/tone — applied across the 10 sample posts already drafted
- Anti-repetition — not yet mechanically tracked; once real posts start publishing, worth adding a "recent hooks/structures used" log (could live as a new tab in `linkedin_content_system.xlsx`) so future drafts can be checked against it automatically

---

## 47-48. Comment output format / post output format

Comment format already defined in `LinkedIn_Comment_Intelligence_System.md` Section 37.

Post output format (new, from this spec) — going forward, every finished post gets delivered as:
```
POST TYPE: [TOFU/MOFU/BOFU/CREATOR/etc.]
TOPIC: [Topic]
HOOK: [Hook]
POST: [Full post]
HASHTAGS: [Relevant hashtags]
FIRST COMMENT: [Prepared text, or "N/A — Not needed" per LinkedIn_Author_First_Comment_System.md]
WHY THIS WORKS: [Short explanation]
SOURCE/INSPIRATION: [Source if applicable]
ORIGINALITY: [Why this is different]
CONFIDENCE: [HIGH/MEDIUM/LOW]
```
This is stricter than how the 10 sample posts were presented (they had series/tier/source tags but not this full block). Applying this format from the next batch onward, unless you'd rather I retrofit the existing 10 into it too. The FIRST COMMENT field was added once `LinkedIn_Author_First_Comment_System.md` was introduced — retrofit not needed for Experiment 001 (already scheduled text-only, no first comment prepared for it yet; can be added before it publishes if you want one).

---

## 49-51. Final AI-slop check, fact check, human check

Same checklists already run informally on the 10 sample posts and the two research docs; now formalized as the mandatory pre-delivery gate for everything — posts, comments, and research alike.

---

## 52. 30-day content machine — math updated for the 3/day cadence

At 3 posts/day, 30 days = 90 posts, not 150 (the 150 figure assumed the earlier 5/day cadence). Per `LinkedIn_Self_Learning_System.md`, this shouldn't be planned as one 90-post block anyway — it's built and reviewed in 9-post experiment batches (10 batches to cover 30 days), each analyzed against `LINKEDIN_LEARNING_MEMORY.md` before the next batch is designed. Not yet started — first step is Experiment 001 (see the memory file's "Next Experiments" section) once you're ready to publish the first batch.

---

## 53-54. Analytics learning loop + experimentation

Not yet applicable — no posts have been published with tracked analytics yet (the one flagship post is still sitting in the composer, unpublished, per the earlier session). Once real posts go out and you can share impressions/likes/comments/shares/saves/profile views/followers, this loop becomes active. The `linkedin_content_system.xlsx` Content Database sheet already has the right columns to extend for this.

---

## 55-56. Core standard and most important rule

Unchanged, and the actual throughline of everything built in this project so far:

REAL DATA > MORE DATA · REAL INSIGHT > GENERIC ADVICE · ORIGINAL THINKING > REWRITING · SPECIFICITY > FLUFF · RELEVANCE > POPULARITY · QUALITY > QUANTITY · AUTHENTICITY > OPTIMIZATION · HUMAN VOICE > AI TEMPLATE · TRUST > VIRALITY · USEFUL COMMENTS > MORE COMMENTS · REAL EXPERIENCE > FAKE PERSONAL STORIES · PRIMARY SOURCES > SECONDARY SUMMARIES

If there's nothing valuable to say: say nothing. If there's nothing useful to comment: don't comment. If a source can't be verified: don't present it as fact.