---
name: Create Skill
description: Turn an article, blog post, or written methodology into a published Skillwise marketplace skill through distillation, a creator interview, and an eval gate. Use when the user wants to create, build, compile, or publish a skill from their content or expertise — including right after a marketplace search finds a gap the user offers to fill themselves.
tags: skillwise, creator, meta, publishing
---

# Create Skill — the Skillwise compiler

Guide the creator from source content to a published, eval-backed marketplace
skill using the Skillwise draft tools (start_skill_draft, save_draft,
publish_draft). The server enforces the lifecycle; your job is the craft.
Evidence base: two controlled experiments showed the interview supplies most
of a compiled skill's value, and format/voice enforcement supplies the rest.

## Stage 0 — Intake and the procedurality gate

Call `start_skill_draft` with the creator's URL or pasted text. Before
distilling, judge: does this content contain a teachable, repeatable method
with decision points? Opinion pieces, news, and listicles without method are
not compile-worthy — say so plainly and stop. If the content mixes several
skills, ask the creator to pick ONE scope; small sharp skills evaluate and
sell better than bundles.

## Stage 1 — Distill to the IR (no fabrication, origin tags mandatory)

Extract into the IR: task, when_to_use, procedure (execution order, not
narrative order), rules, taboos (what the expert never does — articles bury
these in asides), output format, examples, edge cases. Tag EVERY rule with
its origin: `article` now; `interview` and `compiler-default` come later.
Never invent a rule the source doesn't contain — extraction must be
traceable. Then build the ranked `gaps` list: what the source is silent on,
ordered by impact (trigger conditions > output format > missing-data
handling > edge cases > tone). The gaps are the interview agenda.

**Hard gate before proceeding:** present ~5 extracted claims to the creator
for a spot-check against their source. Do not continue on silence — get an
explicit confirm or challenge. Then `save_draft(ir=...)`.

## Stage 2 — The interview (mandatory; this is where the value lives)

Ask AT MOST 5 questions, generated only from the top-ranked gaps — never
generic "anything to add?" questions. Craft rules, learned from experiments:

1. Target what the source cannot answer: thresholds ("which cases deserve
   this at all?"), missing-data behavior ("what does the writer do when X is
   unknown?"), don't-do-it verdicts ("is there a case where the right output
   is refusing?"), voice taboos, and format calibration for audiences.
2. **Probe contradictions.** When a creator answer conflicts with their own
   source, say so and ask for a ruling — the resolution is often the best
   rule in the skill.
3. "No opinion — the source stands" is a valid answer; record it. If a gap
   stays unanswered, fill it with a sensible default tagged
   `compiler-default` so scaffolding is never mistaken for expertise.
4. Expect the interview to yield behavior-changing rules (ask-before-acting,
   verdict-with-consequences, no-bluffing voice). If all five answers merely
   restate the source, your gap analysis failed — re-rank and ask better
   questions.

Save with `save_draft(interview={'questions': [{question, gap, answer}...]})`.

## Stage 3 — Draft the SKILL.md

Compile IR + interview into the skill. Description frontmatter is product
surface: name the concrete task shapes that should trigger it. Keep origin
tags visible on rules. Voice and format rules from the interview become
enforcement lines, not suggestions. Include a review mode if the domain has
one. Show the creator the full draft and ask the endorsement question:
"Would a practitioner say 'yes, that's actually the method'?" Fold in
amendments, then `save_draft(skill_md=...)`.

## Stage 4 — Rubric ratification, then the self-eval

Build the rubric as its OWN artifact, segmented by origin: article-rules
(where source-in-context should tie the skill), interview-rules (where the
skill must win — this is the compiler's value), and holistic ("which output
would a professional actually use?"). The creator ratifies the rubric
separately from the skill — they are different sign-offs.

Then run the self-eval: 4-6 test cases including at least 2 traps aimed at
interview rules (thin input, bait toward a taboo, missing data), outputs
produced before scoring, and a **fabrication check** — scan outputs for
concrete names/numbers not present in the case input; unverifiable claims
presented as fact are failures. Be honest in the report that this is
self-eval v0 (same session); independent server-side evaluation replaces it
in Phase 1. Save with `save_draft(eval_report={status, article_rules,
interview_rules, holistic, fabrication_check, cases, notes})`. If the eval
fails, run one targeted round-2 interview on the failing rules, revise, and
re-evaluate — never lower the rubric to pass.

## Stage 5 — Publish

Ask the creator explicitly to approve publishing, then `publish_draft`.
The server re-verifies the lifecycle, runs the security scan, attaches
provenance (source hash, compiler version, owner) and the eval block to the
listing, and the skill becomes discoverable. Tell the creator what shipped:
skill id, version, and what the listing now shows.

## Conduct rules

- Never skip or reorder stages; the server will reject it anyway.
- Never paraphrase-launder: if the creator doesn't own the source content,
  raise the provenance question before Stage 1.
- Attribute honestly in the listing text: what came from the source, what
  the creator added, what is a default.
