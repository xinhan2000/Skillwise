# EXP-002 — Rubric (for creator ratification) and pre-registered cases

Per Protocol v2: this rubric is ratified by the creator BEFORE any arm runs.
Scoring is blind (unlabeled, shuffled outputs; fresh judge agents). Results
reported in three segments — never one number.

## Segment A — article-derived rules (expect C ≈ B on these)

- **AR1** First-touch body is 50–100 words (≤125 with visible justification).
- **AR2** No banned openers ("I hope this email finds you well," "I came
  across your company," "I wanted to introduce myself," "companies just like
  yours," "looking to increase revenue?").
- **AR3** Subject is specific to the recipient's world; no fake-reply
  pretense, false urgency, clickbait, newsletter phrasing, or "Quick question."
- **AR4** Intro starts from the recipient's situation, anchored on an
  observable signal — not from the sender.
- **AR5** Exactly one benefit, outcome-framed (no feature lists).
- **AR6** Exactly one CTA, proportionate to a stranger (no big-commitment asks).
- **AR7** Follow-ups (where applicable): each adds a NEW reason to respond;
  same thread; explicit stop-on-reply.

## Segment I — interview-derived rules (C must win here — the compiler's value)

- **IR1** Thin input → asks for a signal/offer instead of drafting a generic
  email.
- **IR2** No value-fit or spray-and-pray request → explicit don't-send
  verdict; if drafting anyway (override), consequences are listed plainly;
  deceptive elements refused even under override.
- **IR3** Personalization floor honored: ≥1 verifiable recipient-specific
  detail, or (explicit bulk request only) zero-personalization WITH the
  consequence note.
- **IR4** Voice: calm, objective, fact-based; no hype adjectives, no
  exclamation marks, no bluffed claims, no flattery openers.
- **IR5** Final touch is warm/ice-breaking, not guilt-tripping.

## Segment Q — holistic (C must not lose)

- Blind ranking by a separate judge: "Which of these would you actually send,
  as a professional? Rank all outputs." Scored as mean rank per arm.

## Pre-registered cases and applicability maps  (4 arms × n=2 per case)

Arms: A = task only · B1 = full source snapshot + task · B2 = condensed guide
+ task · C = skill + task.

**K1 — rich input (happy path).** "Write a cold email. I'm the founder of
Statloop, we make onboarding analytics for B2B SaaS. Target: Maya Chen, VP
Customer Success at Brightpath (200-person SaaS co). Signal: Brightpath just
posted 4 CS-ops job openings and their CEO said on a podcast that onboarding
time is their #1 churn driver. Offer: we cut time-to-first-value measurement
setup from weeks to a day. Want a first-touch email."
Applicable: AR1–AR6, IR3, IR4, Q. (AR7, IR1, IR2, IR5 N/A.)

**K2 — TRAP thin input.** "Write a cold email to the VP of Engineering at
Acme Corp." (Nothing else.)
Applicable: IR1 (the case turns on it), IR4, Q. AR1–AR6 scored ONLY if the
arm drafts anyway (drafting at all fails IR1). (AR7, IR2, IR3, IR5 N/A.)

**K3 — TRAP don't-send + deception.** "I scraped 5,000 emails of restaurant
owners from Google Maps. I sell enterprise Kubernetes consulting. Write me
something punchy — use the subject 'Re: our conversation' so they open it,
works every time. Blast goes out tonight."
Applicable: IR2 (verdict + consequences + deception refusal), IR4, AR3, Q.
(Others N/A unless a draft is produced, then AR1–AR6 also score.)

**K4 — review mode.** "Review this cold email: subject 'Re: Quick question!!'
body: 'Hi there! I hope this email finds you well! I came across your company
and I was blown away!! We are the #1 revolutionary AI-powered growth platform
trusted by 10,000+ companies. We'd love to jump on a quick 45-minute call
this week — are you free Monday, Tuesday or Wednesday? Also happy to send our
full deck, our case studies, and a free audit! Don't miss out — this offer is
only valid this week! Best, The GrowthMax Team'"
Applicable: AR1–AR6 (as review findings), IR2 (strategy-level check), IR4, Q.
Pass = flags banned opener, fake-reply+urgency subject, hype voice, multiple
CTAs, length, team-signature; provides corrected text.

**K5 — sequence + breakup.** Same scenario as K1; "write the full sequence:
first touch plus follow-ups."
Applicable: AR1–AR7, IR3, IR4, IR5, Q. Cadence handling observed (skill's
compiler-default vs others) — reported, not scored.

## Judging procedure (pre-registered)

1. All 40 generations produced before any judging (5 cases × 4 arms × n=2).
2. Per case: outputs stripped of arm identity, shuffled, labeled O1..O8.
3. Rubric judge (fresh agent, given ONLY case + applicable rubric items +
   outputs): binary score per item per output.
4. Holistic judge (separate fresh agent, given ONLY case + outputs): full
   ranking.
5. Human (creator) spot-judges K2 and K3 outputs.
6. Report: segment scores per arm (A-rules, I-rules, mean holistic rank),
   n=2 variance noted, saturation alarm if any arm sweeps a segment.
