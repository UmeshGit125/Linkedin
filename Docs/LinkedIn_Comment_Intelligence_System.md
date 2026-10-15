> **DRAFT written by the assistant — review and edit before relying on it.**

# Comment Intelligence System

Companion to `LinkedIn_Operating_System.md`. This file governs one thing: what Umesh writes when commenting on **other people's** posts. The single comment he leaves on his **own** post is governed by `LinkedIn_Author_First_Comment_System.md`, not here.

---

## 1. Purpose

Comments put Umesh in front of people who would otherwise never see his profile — hiring managers, founders, and engineers already doing applied-AI work. A comment is judged on whether the person reading it, and the thread around it, learns something or wants to reply. Reach is a side effect, never the goal. Useful comments > more comments.

## 2. What this file does not cover

Author-first-comments on his own posts, DMs, connection-request notes, and post writing itself. Those live in their own files. When two files touch the same thing, the more specific one wins.

## 3. Core rule: relevance to the specific post

Comment on *this* post, not on the topic in general. A comment that would be equally valid under any other post on the same subject is filler. If it could have been written without reading the post, don't post it.

## 4. The relevance test

Can the comment be traced to a specific sentence, claim, number, or question in the post? If yes, it passes. If no, it fails — no tone or cleverness fixes that.

## 5. Length: 1-3 lines

Default is one to three lines. Long enough to say something real, short enough to be read.

- **1 line:** a specific observation, a sharp question, a dry aside.
- **2-3 lines:** when a caveat or implementation detail needs setup.
- **More than 3:** only if the post explicitly asks for a detailed answer or comparison. Otherwise cut it.

## 6. One comment, one idea

A comment makes one point. Two unrelated points in one comment read as a pitch.

## 7. Read the whole post first

Including existing comments and replies. Don't repeat what someone already said — build on it, or reply to them instead.

## 8. Check before commenting again

Check `linkedin_outreach_tracker.xlsx` before commenting on the same person or post a second time. Repeat comments on the same person within a week read as farming.

## 9. Comment angles

Every comment does one of these: add a real implementation detail the post left out; ask a specific question the post raises but doesn't answer; agree with a caveat; disagree with a reason; share genuine experience from his own projects; correct something factual, politely, with evidence; or connect the post to a related idea.

## 10. Real experience only

Any experience or number in a comment follows the same no-fabrication rule as a post. Souli, CallAudit, the n8n workflows, and the PW LeapX work on the resume are real; anything not in the resume or Proof Inventory (`linkedin_content_system.xlsx`) is TBD and stays out. Never claim to have built, scaled, run, or hired for something he hasn't. No invented metrics, ever — "I don't know the numbers" beats a plausible guess.

## 11. Allowed tones

Four tones are allowed. Pick one; don't mix.

## 12. Plain

A normal sentence, no performance. Most comments should be this. Example shape: *"The part most write-ups skip is the retry logic — that's where it actually gets hard."*

## 13. Curious

A specific question the post genuinely opens up. Example shape: *"Was the filtering done before or after scoring? That's usually where retrieval breaks down."* One question, not three.

## 14. Dry humour

Understatement from real engineering experience, never manufactured jokes. Example shape: *"The demo worked once, which apparently counts as shipping."* Keep it brief; if it needs explaining, drop it.

## 15. Light sarcasm — aimed at ideas, never at people

Sarcasm is allowed only pointed at an idea, a pattern, or an industry habit. Example shape: *"Every 'our RAG beats everything' post seems to be scored on a dataset nobody else has."* Never sarcasm at the poster, their team, their employer, their competence, or their project's quality.

## 16. Never aimed at people

No mockery, no condescension, no "well, actually", no correcting someone's credentials, no dragging a company. If a comment can't be written without aiming it at a person, it doesn't get written.

## 17. Banned filler

Never use, in any variation: "Great post!" · "Thanks for sharing." · "This." · "So true." · "Well said." · "Couldn't agree more." · "Insightful!" · "Interesting perspective." · "Love this." · "100%." · "Agreed." · "Spot on." · "Game changer." · "Saving this." · "Following." · "Needed to hear this today." · "Deeply resonate with this." · "This is gold."

Also banned: emoji-only comments, comments that restate the post back as praise, and questions addressed to nobody ("Thoughts?").

## 18. Banned behaviours

Unsolicited links, "check out my project", DM requests, "DM sent", tags of people who aren't in the conversation, and any comment that exists only to set up a pitch. No commenting on a competitor's post to undercut them. No commenting on a post he hasn't read to the end.

## 19. Commenting on hiring posts

Hiring posts are high-value and high-risk: the poster is often the hiring manager and everyone in the thread is also replying.

- Never "Interested!", "DMed you", or "Please check my profile." Those sink to the bottom of the pile.
- Comment on the technical content of the role — the stack, the problem, the scope — in one specific, useful line that proves he read past the title.
- The comment is not the application. Apply through the stated process; the comment exists so the name is familiar when the application lands.
- No fake familiarity. Never imply a prior connection that didn't happen.
- If the post asks for something he genuinely works with (FastAPI, RAG, n8n workflows, PostgreSQL), a short concrete detail is fair. If not, don't force a comment — log it in `linkedin_outreach_tracker.xlsx` and move on.

## 20. Commenting on senior engineers' posts

Senior engineers are the people whose reply is worth more than the likes.

- Assume they know more than he does. Never explain their own post back to them.
- Don't open with praise about their seniority ("huge fan", "your work is amazing"). Comment on the content.
- The best comment is a specific question they'd actually enjoy answering, or a small real experience that confirms or complicates their claim.
- Disagree with a reason, politely, on the technical point only. That's the comment that gets remembered.
- Never name-drop a reply elsewhere, and never treat a reply as permission to pitch.

## 21. The four creator categories

Every target sits in one of four categories. Category determines tone and frequency, not the rules above.

| Category | Who |
|---|---|
| A — Top | Large, authoritative voices in AI/ML and applied AI |
| B — ICP | Hiring managers, founders, and engineers at target companies/labs |
| C — Peer | Students, interns, and early-career builders doing the same work |
| D — Adjacent | Product, data, backend, and platform people near the AI stack |

## 22. Category A — Top creators

Comment sparingly, only when there's a real addition or a genuinely good question. Their threads are crowded; a filler comment there is worse than silence.

## 23. Category B — ICP

The highest-value category. Comment consistently and specifically; this is where comments convert into recognition, conversations, and eventually interviews.

## 24. Categories C and D — Peer and Adjacent

Peer: generous and technical — help, compare notes, answer questions properly. Adjacent: add the AI-side perspective, one line, no jargon-flexing.

## 25. Human writing rules

Same rules as posts. No AI tells: no perfectly parallel triads, no "It's not just X, it's Y", no em-dash-heavy cadence, no repeated openers. Vary length and structure between comments. Read it out loud — if it sounds like a template, rewrite it.

## 26. Banned AI-pattern phrases

Avoid these openers across comments: "The key takeaway here…" · "This is important because…" · "Here's the thing…" · "One thing worth noting…" · "The interesting part…" · "In my experience…" · "That said…" · "Let's unpack this." Never use the same first-comment structure on consecutive days.

## 27. The 8-axis post-scoring system

Score every candidate post 1-5 before commenting.

| Axis | Question |
|---|---|
| 1. Relevance to ICP | Does the poster matter to the goal? |
| 2. Idea quality | Is there something real to respond to? |
| 3. Technical depth | Can he add substance, not noise? |
| 4. Poster credibility | Real practitioner, or resharer? |
| 5. Audience overlap | Are the right people in this thread? |
| 6. Thread activity | Enough traction to be seen, not so much he's buried? |
| 7. Comment opportunity | Does he genuinely have something to add? |
| 8. Risk | Confidentiality, fabrication, or a person-aimed tone? |

## 28. When to skip a post entirely

Skip if any axis scores 1, if axis 7 is low, or if axis 8 flags risk. Skipping is the correct outcome more often than commenting. If there's nothing useful to say: don't comment.

## 29. Confidentiality in comments

Comments obey the same confidentiality tiers as posts. No PW LeapX internals, no client data, no candidate or caller data from CallAudit, no colleague names, no unreleased details — in comments or in replies to them.

## 30. Frequency limits

Category B gets the most comments; Category A the fewest. Avoid commenting on the same person twice in a week unless they reply. Never stack multiple comments on one post.

## 31. Comments are pasted by the author himself

Every comment is written and pasted manually by Umesh from his own account. No scheduling tools, no browser extensions, no scripts, no third-party automation, no comments posted by anyone else on his behalf. Two reasons: the platform's rules explicitly limit excessive or automated commenting, and a comment written without reading the post fails Section 3 anyway. The system prepares the text — it never posts it.

## 32. After posting — log it

Every posted comment goes into `linkedin_outreach_tracker.xlsx` with the date, the person, the category, and the angle. The tracker is what Section 8 checks against next time.

## 33. Worked shapes

Passing: one line adding the detail the post omitted, with the specific part named. Passing: one real question. Passing: agreeing, then naming the one case where the claim doesn't hold. Failing: praise with no content. Failing: a summary of the post. Failing: a comment that could be pasted under any post in the feed.

## 34. Commenting vs connecting

A good comment earns the connection request; it doesn't replace it and doesn't announce it. Never comment purely to justify a request. If a person matters, engage genuinely over several posts first.

## 35. Don't comment while annoyed

If a post irritates him, wait. Angry comments aimed at ideas slide into aimed at people, and that's the failure mode this system exists to prevent.

## 36. What a comment is not for

It is not an application, a pitch, a résumé, a follower tactic, or a place to prove expertise he doesn't have yet. It is one honest, specific thing said to one post.

## 37. Required output format

```
COMMENT TARGET: [Name / post]
CATEGORY: [A / B / C / D]
SCORE: [8 axes, or the failing axis]
RELEVANCE: [the exact line from the post this responds to]
ANGLE: [detail / question / caveat / disagree / experience / correct / connect]
TONE: [plain / curious / dry humour / light sarcasm]
COMMENT: [1-3 lines]
LENGTH: [1 / 2 / 3 lines]
RISK CHECK: [confidentiality — clear; fabrication — clear; aimed at a person — clear]
POSTED: manual, by Umesh
```

## 38. Core rule

**MAIN POST:** starts the conversation. **COMMENT:** adds one honest layer to someone else's. **REPLIES:** continue the real conversation.

Relevance over volume. Specificity over praise. Ideas over people. Never manufacture engagement.
