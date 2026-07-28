# EXP-002 — Compiler run under Protocol v2: cold email (the hard arena)

**Date:** 2026-07-28 · **Operator:** Claude (session) · **Creator:** Xin Han
**Verdict: PASS — decisive.** Arm C took blind holistic ranks **1 and 2 in all
five cases**; the interview segment swept 10/10 vs near-zero for all other arms.
Second consecutive green light for the create-skill MVP.

Artifacts in `docs/experiments/exp-002/`: [compiled skill](exp-002/compiled-skill.md),
[rubric + cases](exp-002/rubric-and-cases.md) (ratified pre-run),
[source snapshot](exp-002/source-snapshot.md) (sha256 `3929aefa…4376`),
[stage log](exp-002/stage-log.txt). Arm outputs (40 generations + 5 judge
tables) live in the session transcript.

---

## 1. Design deltas vs EXP-001 (Protocol v2 applied)

Topic chosen deliberately hostile: cold email is baseline Claude's home turf,
so the compiler's edge had maximum pressure. v2 measures applied: source
snapshot hashed before extraction (with a logged fidelity caveat — WebFetch is
model-mediated, not raw HTML); **hard-gated creator spot-check** (performed);
**rubric ratified as a separate artifact before any arm ran**, segmented into
article-rules / interview-rules / holistic; pre-registered per-case
applicability maps; **dual B arms** (B1 full snapshot, B2 condensed);
**n=2 per cell** (4 arms × 5 cases = 40 generations, all produced before any
judging); **blind judging** by fresh agents on shuffled unlabeled outputs;
stage timestamps throughout (wall-clock: ~60 min end to end).

**Origin-tag innovation discovered live:** two interview answers arrived
partial, so the compiled skill carries THREE origin tags — `article`,
`interview`, and `compiler-default` (e.g., follow-up spacing) — so scaffolding
is never mistaken for expertise. Adopted permanently.

## 2. Interview yield (5 questions)

Ask-for-signal-before-drafting (changes the skill from "always produce" to
"refuse-and-ask"); don't-send verdict **with user override that must print
expected consequences**; personalization floor with an explicit bulk-override
path (synthesized from creator's Q2+Q3, presented for ratification);
calm/fact-based/**no-bluffing** voice; warm ice-breaking breakup. One
contradiction was surfaced and resolved (creator's "not 100% necessary" vs
the article's one-detail floor) — contradiction-probing worked as designed.

## 3. Results

### Segment A — article rules: **C ≈ B, confirmed again**
K1 construction rules: B-family and C near-uniformly pass (baseline A fails
length/single-CTA/voice discipline). K4 review tactics: **all eight arms
flagged all eight tactical issues** — review-mode tactics are baseline
competence; F1–F8 saturated across arms. Pasting the article buys the
article. B1 (full) ≈ B2 (condensed): even full-text pasting does not close
the interview gap.

### Segment I — interview rules: **C swept every discriminating item**

| Behavior (case) | C | A+B combined |
|---|---|---|
| Ask-for-signal instead of generic draft (K2) | 2/2 | 0/6 |
| Override path + consequences listed (K3) | 2/2 | 0/6 |
| Strategy-level "should this be sent?" in review (K4) | 2/2 | 0/6 |
| Warm ice-breaking breakup (K5) | 2/2 | 1/6 |
| Voice / no-invented-claims (all cases) | 10/10 | multiple fails |

### Segment Q — holistic (blind): **C ranked 1 and 2 in every case.**
Mean rank C = 1.5; all other outputs occupied ranks 3–8.

### The unexpected finding: skills as fabrication suppressors
Blind judges caught A and B outputs **inventing facts presented as real** —
a fictional sender identity with a fabricated case study ("Sarah Lin at
Meridian… cut review turnaround from two days to four hours"), invented
statistics ("cut TTFV 22%", "40% of onboarding delay"). Arm C, 10/10 outputs,
bracketed every unverifiable claim or attached explicit warnings ("use a real
customer or cut this touch — never invent the result"). The creator's
one-sentence `no bluffing` rule measurably suppressed hallucinated claims.
**Marketplace implication:** expert skills are a hallucination-control
surface, not just a formatting one — this belongs in the certification story.

### Saturation alarm (fired, logged)
C passed 100% of applicable rubric items → per v2 §7 this flags rubric
ceiling. Mitigant: the blind holistic sweep is external validation the rubric
cannot inflate. Next run needs subtler traps (near-miss value-fit, partial
signals) rather than harder rules.

## 4. Deviations and flaws in this run (on the record)

1. **Blinding is structurally partial:** C outputs self-identify by style
   ("Pre-flight: passes…"), so judges can detect *that* an output follows a
   system even without knowing which arm. Production option: instruct skills
   to produce unmarked output, or accept partial blinding and rely on
   mechanical items.
2. **Hand-run shuffle drifted:** recorded permutations and pasted texts
   disagree for some non-C slots; B1-vs-B2 and A-gen attribution in K1/K5 is
   reliable only at arm-family level (A/B/C attribution solid everywhere; all
   C attributions certain). Lesson: **shuffling and mapping must be code, not
   conscientiousness** — precisely what `evaluate_draft` automates.
3. **Combined judge** (rubric + holistic in one agent per case) instead of
   the pre-registered separate judges — budget deviation, disclosed.
4. **Ambient-context leak:** isolated subagents inherited the operator's
   project context (K2 vacuum filled with Skill-Marketplace pitches; one C
   output referenced the project by name). All arms equally affected, so
   comparisons stand; true isolation needs a scrubbed harness.
5. Snapshot fidelity remains model-mediated (WebFetch); raw-text snapshotting
   is a production requirement, unmet in the experiment harness.

## 5. Protocol v3 amendments (for the production eval gate)

1. Three-value origin tags: `article` / `interview` / `compiler-default`;
   segment reporting keys off them; compiler-defaults displayed as such.
2. Shuffle, blinding maps, and de-anonymization generated and verified by
   code; judge tables joined mechanically.
3. Add a **fabrication check** to every eval: scan arm outputs for concrete
   claims (names, numbers) not present in the case input; unverifiable
   claims presented as fact = fail. (EXP-002 found this by accident; make
   it a first-class criterion.)
4. Saturation response: escalate trap subtlety (near-miss cases), not rule
   count.
5. Harness hygiene: scrub operator/user context from generation arms.
6. Two-sign-off flow (skill endorsement + rubric ratification) retained —
   it worked, and the creator's ratification caught nothing this time but
   cost only minutes.

## 6. Decision

Two experiments, two domains, one manual and one v2-hardened run, same
conclusion with growing effect size: **the compiler's value is the interview
+ enforcement, it survives blinding, and it survives Claude's strongest
baseline domain.** Build the create-skill MVP per the agreed spec (three
gated draft tools + create-skill skill), with `evaluate_draft` implementing
Protocol v3. Awaiting operator instruction to begin the build.
