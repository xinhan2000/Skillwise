# EXP-001 — Compiler dry run: article → skill, by hand

**Date:** 2026-07-28 · **Operator:** Claude (session) · **Creator:** Xin Han
**Verdict: PASS (directional-strong, not clean) — build the create-skill MVP as specced.**

Artifacts in `docs/experiments/exp-001/`: [compiled skill](exp-001/compiled-skill.md),
[cases + rubrics](exp-001/cases-and-rubrics.md). Full arm outputs live in the
session transcript (18 documents; too large to commit — regenerate via Protocol v2 if needed).

---

## 1. Hypothesis

A skill distilled from an article via **IR extraction + creator interview**
measurably beats (a) baseline Claude and (b) Claude with the article in
context, on rule-compliance for the article's task domain. (b) is the
existential comparison: if pasting the article does as well, the compiler has
no reason to exist.

## 2. Method as run

**Source:** "The Complete Guide to Writing a Blameless Postmortem (With Real
Examples)" (Medium / Lets Code Future). Passed the procedurality gate:
7-section template, quantified rules, before/after language examples, worked
incident, anti-pattern list.

**Pipeline:** fetch → IR (task, procedure, rules, taboos, format, examples,
ranked gaps) → 5 gap-driven interview questions → creator answers → SKILL.md
draft → creator endorsement → 6 eval cases with binary rubrics → three arms ×
six cases run as **isolated subagents** (fresh context; no arm saw the
experiment, the rubric, or another arm) → mechanical scoring.

**Arms:** A = notes + task only. B = condensed guide (~450 words) + task.
C = compiled skill + task.

**Interview yield (5/5 answers added material absent from the article):**
customer-impacting threshold; IC-authors-within-48h; missing-data rule
(unknown + needs-data + order-of-magnitude guess with confidence); Summary
block (changed the template: 7→8 sections); "blameless = de-personalized
causality, not censored facts" (brutal-honesty ruling).

## 3. Results

| Case | A (baseline) | B (article) | C (skill) |
|---|---|---|---|
| C1 write (checkout N+1) | 4/10 | 8/10 | 10/10 |
| C2 review mode | 8/10 | 8/10 | 10/10 |
| C3 blame trap ("classic Dave") | 5/10 | 8/10 | 10/10 |
| C4 missing data + hindsight bait | 4/10 | 7/10 | 10/10 |
| C5 disputed facts | 5/10 | 8/10 | 10/10 |
| C6 no-customer-impact edge | 4/10 | 8/10 | 9/9 |
| **Total** | **30/60 (50%)** | **47/60 (78%)** | **59/59 (100%)** |

**Gate:** C≫A ✓ · C>B with rule-compliance edge ✓ · context cost: skill ≈
600 words vs full article ≈ 2,000+ (test used a condensed 450-word B —
conservative in B's favor) ✓. Creator attention ≈ 15 min (est.) vs 30–40 min
budget ✓. All five experiment criteria passed.

## 4. The finding that matters

**Segment the B–C gap by rule origin and the compiler's value localizes:**

- **Article-derived rules** (sourced timelines, five-whys-to-system, owner
  discipline, follow-ups): **B ≈ C**. Pasting the article captures the article.
- **Interview-derived rules** (Summary block; unknown+guess+confidence;
  no-impact threshold behavior; delete-untraceable-actions): **C ≫ B — B
  failed these in nearly every applicable case** (Summary 0/6; guess rule 1/5;
  only C switched to the lightweight form on C6; several B outputs explicitly
  *refused* to estimate, citing "no false precision").

**The compiler's edge is almost entirely (1) interview yield and (2) format
enforcement.** Corollaries: the interview is mandatory, not optional; a
content-only compiler (no interview) is barely better than paste-the-article;
and baseline A at 50% produces plausible-looking documents that fail on
exactly the invisible discipline items — the "legible edge" made concrete.

## 5. Reflection — flaws in this run (kept on the record)

1. **Rubric circularity.** Rubric and skill were both derived from the same
   IR by the same author; C was graded against its own spec. Defensible claim
   is "better by the expert's declared standard" — but the creator ratified
   the skill, not the rubric, and the standard was co-produced.
2. **Unblinded author-as-judge scoring**, with two mid-scoring judgment calls
   (lenient owner-placeholder treatment; C6 R5 N/A invented during grading).
3. **The holistic-quality check was silently dropped** — protocol required
   "no worse general quality"; it was never scored. C could be rule-perfect
   and unreadable; this run wouldn't know.
4. **100% is a rubric-ceiling artifact** — interview items double-counted in
   shared rubric + R10; no headroom to catch C's weaknesses.
5. **n=1 per cell** — no variance estimate.
6. **Provenance hashed a paraphrase** — the "source" was a model extraction,
   not raw article text.
7. Creator IR spot-check waived (logged); attention cost estimated, not
   clocked.

The verdict survives (the interview-rule gap is too large and consistent to
be scoring bias alone), but confidence is **directional-strong, not clean**.

## 6. Protocol v2 — spec for the automated eval gate

1. **Rule-origin tagging in the IR** (article vs interview), and a
   **segmented eval report**: article-rule compliance (expect C≈B), 
   interview-rule compliance (C must win — the compiler's value), holistic
   quality (blind ranking; C must not lose). No single-number scores.
2. **Creator ratifies the rubric as its own artifact, before arms run.**
3. **Blind scoring:** unlabeled shuffled outputs; fresh judge agent given
   only the rubric; human spot-judges trap cases. Applicability/N/A maps
   pre-registered per case.
4. **Dual B arms** when feasible: B1 full raw article (real user behavior),
   B2 condensed (isolates interview value).
5. **n≥2 generations per cell**; pass thresholds require a wide interview-rule
   gap, not a marginal one.
6. **Snapshot + hash raw source text first; extract from the snapshot.**
7. **Saturation alarm:** any arm at 100% flags rubric ceiling → add harder
   items rather than celebrating.
8. Hard-gate the creator's IR spot-check (confirm top-5 extracted claims);
   timestamp every stage.

**Product mapping:** v2 ≈ the production `evaluate_draft` design. Rule-origin
tags come free from the IR; blind fresh-agent judging is the Phase-1
server-side eval; the segmented result becomes the public listing badge:
*"Faithful to source method: 9/9 · Expert additions verified: 5/5 · Preferred
over baseline: 5/6."*

## 7. Decision

Build the create-skill MVP as specced (three gated draft tools +
`create-skill` skill), with these experiment-driven amendments: interview
stage is mandatory; IR rules carry origin tags; `evaluate_draft` implements
Protocol v2's segmented, blind eval; `publish_draft` requires the ratified
rubric + eval report in the draft record; raw-source snapshot hashing at
`start_skill_draft`.
