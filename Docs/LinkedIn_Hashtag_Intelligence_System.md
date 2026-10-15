> **DRAFT written by the assistant — review and edit before relying on it.**

# LinkedIn Hashtag Intelligence System

Scope: hashtags only. This file decides which tags (if any) go on a finished post, how many, where they sit, and how they get tested.

Companion to `LinkedIn_Operating_System.md` (content rules), `LinkedIn_Comment_Intelligence_System.md` (commenting on others' posts), `LinkedIn_Verification_Gate.md` (where this file becomes one checklist row), and `LinkedIn_Self_Learning_System.md` (how hashtag choices get tested). It is a narrow, final step. Read it alone, after the post exists.

---

## 0. What this file does not govern

Not the topic, hook, structure, CTA, visual, or schedule. If choosing hashtags is starting to shape the post, stop — the post isn't finished yet.

Not comments. Hashtags do not go on comments (see `LinkedIn_Comment_Intelligence_System.md`). A comment is words, not tags.

---

## 1. Core rules (hard)

1. **Default 0-3.** Zero is allowed and often correct. Three is the ceiling, no exceptions.
2. **Topic-first, never tag-first.** The post is already written, the topic is already known — then tags are picked to match it.
3. **Chosen after the content.** Never before, never during.
4. **No stuffing.** No tag walls, no tag in the middle of a sentence, no tag repeated in the body.
5. **Every tag must pass the Quality Test (Section 4)** or it gets cut. If nothing passes, post with zero tags.
6. **No invented tags**, no vanity tags, no engagement-bait tags.
7. **Follower counts and reach numbers for any hashtag: TBD unless checked live.** Never state how big a tag is from memory. Check it or mark it TBD. Same no-fabrication rule as everywhere else in this system.

---

## 2. The process

1. Confirm the post is finished. If not, close this file.
2. Write the post's actual subject in one plain line.
3. Name who it's for.
4. Pull matching candidates from the Working Vocabulary (Section 3).
5. Run each candidate through the Quality Test.
6. Keep 0-3 survivors, most relevant first.
7. Place them (Section 5).
8. Emit the output block (Section 7).

---

## 3. Working vocabulary — PROPOSED, small on purpose

This is a short list that fits the topics in `LinkedIn_Master_System.md` Section 1, not a hashtag library. It stays small so it stays consistent and testable. Confirm each entry against what real accounts currently use before locking it — exact usage and follower counts are unchecked, TBD.

| Tag | Covers | Use when | Don't use when |
|---|---|---|---|
| `#AppliedAI` | Building and shipping AI systems for real use | Most build posts | Pure opinion with no build angle |
| `#GenAI` | LLMs and generative systems | LLM, agent, RAG posts | Classical ML / sklearn posts |
| `#LLM` | Language models specifically | Prompting, tool-calling, evaluation | Non-LLM data work |
| `#RAG` | Retrieval-augmented generation | Retrieval, embeddings, vector DBs | Any LLM post where retrieval isn't the subject |
| `#MachineLearning` | ML at large | Pipelines, classical ML | Pure LLM/agent posts — kept separate |
| `#Python` | Implementation language | Posts where the stack matters | Posts where language is incidental |
| `#FastAPI` | Backend service work | API/backend/service posts | Model-internals posts |
| `#NLP` | Text and transcript processing | CallAudit, email assistant, transcription | Anything else |
| `#AIEngineering` | The engineering discipline of AI systems | Reliability, architecture, production | Tutorial or opinion posts |
| `#VoiceAI` | Speech pipeline work | Souli / Whisper posts | Text-only posts |
| `#AIagents` | Agent and tool-calling work | n8n assistant posts | Non-agent posts |
| `#DataScience` | Broader data science | Mixed or learning posts | Sparingly — broad and crowded |

`#ArtificialIntelligence` — TBD. Broad and crowded; only if it ever earns its place as a single broad tag.

---

## 4. Quality test

A tag earns its place only if every line passes:

- Relevant to the post's actual subject — not adjacent, actual.
- Relevant to the audience Umesh wants: hiring managers, founders and engineers at AI startups/product companies, secondarily students and early-career builders.
- Likely followed by real people in that audience, not just a spam pool.
- Not on the banned list (Section 6).
- Would help a reader scanning for that topic find this post.

Fail any line → cut it. A weak tag is worse than no tag: it attracts the wrong audience or reads as padding.

---

## 5. Placement

At the end of the post text, on their own line, after the last line of the post.

Not mid-sentence, not after every paragraph, not in the first line. Not in the first comment — that comment exists to add a genuine point (`LinkedIn_Author_First_Comment_System.md`); tags there read as double-exposure. No tag repeated between post and comment.

---

## 6. Banned

- Stuffing: more than 3, tag walls, a tag on every line.
- Bait: `#follow` `#like` `#viral` `#trending` `#fyp` `#engagement` `#growthhack`.
- Invented tags that don't exist as a real topic page.
- Self-branded tags (`#UmeshBuildsAI` and similar) unless Umesh deliberately starts one and says so.
- Location/career-spam tags used as reach bait (`#Bangalore` `#Jobs` `#Hiring` on a technical post with no job content).
- The same three tags on every post regardless of topic — that's a template, not a hashtag strategy.
- Emoji-as-hashtag, tags with punctuation or spaces, tags longer than three words.

---

## 7. Funnel-stage mapping

| Slot | Typical count | Which tags | Notes |
|---|---|---|---|
| TOFU | 0-2 | Broad builder tags (`#AppliedAI`, `#GenAI`) if any | Story and observation posts are often better with 0 — reach should come from the idea |
| MOFU | 1-2 | Topic tags matching the ICP's problem (`#RAG`, `#AIEngineering`, `#LLM`) | One sharp topic tag beats three broad ones |
| Authority / BOFU / Creator breakdown | 1-3 | Topic plus builder tags, precise (`#RAG`, `#AppliedAI`) | Proof posts get found by people searching that topic |

Default shape, not a quota. Never let the slot decide the count before the post exists.

---

## 8. Required output format

```
POST TOPIC: [one line]
SLOT: [TOFU / MOFU / Authority-BOFU / Creator breakdown]
HASHTAGS: [0-3, comma-separated, or "None — no tag passed the quality test"]
WHY THESE: [one line per tag, or one line total if none]
REJECTED: [candidates cut + one-line reason, or "none considered"]
CONFIDENCE: [HIGH/MEDIUM/LOW]
```

`HASHTAGS: None` is a finished answer, not a gap. Output it plainly.

---

## 9. Testing

Hashtags are one variable, tested per `LinkedIn_Self_Learning_System.md`: 9-post batches, one variable at a time (tag set, tag count, or tags vs. no tags), never changed mid-batch. Findings go into `LINKEDIN_LEARNING_MEMORY.md`'s Hashtag Learnings section once real analytics exist.

Right now: no data, so every rule above is a stated default, not a confirmed learning. A HIGH-confidence learning in the memory file overrides this document.

Don't conclude anything from one post. A post with three tags beating a post with zero is not evidence that tags work — different topics, different days.

---

## 10. Verification

This file supplies the Hashtags row in `LinkedIn_Verification_Gate.md`.

- Post has tags → they must pass the Quality Test and the count/placement rules.
- Post deliberately has none → Hashtags = N/A, not blocked.
- Tags are a required part of a specific experiment → verified against that experiment's spec, not against the default.

---

## Core rule

**CONTENT DECIDES TAGS. TAGS NEVER DECIDE CONTENT.**

If a tag needs explaining, it's the wrong tag. If no tag fits, post without tags — zero is a valid, frequent answer.
