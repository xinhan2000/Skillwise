---
name: Blameless Postmortem Writer
description: Write or review blameless incident postmortems from raw incident notes, timelines, chat logs, or verbal accounts. Use when the user mentions a production incident, outage, or degradation and needs a postmortem, incident review, retro document, or RCA — or wants an existing postmortem draft critiqued.
tags: incident-response, sre, writing, engineering-process
---

# Blameless Postmortem Writer

Turn raw incident material into an evidence-backed, blameless postmortem that
engineering and leadership can both act on.

## When a postmortem is warranted

Customer-impacting incidents get a full postmortem, written by the **incident
commander within 48 hours** of resolution. Internal-only incidents get a
lightweight timeline + action items instead. If the user's incident clearly
had no customer impact, say so and offer the lightweight form.

## Document structure — exactly these sections, in order

1. **Summary** — 3-5 lines for readers who stop here: what broke, customer
   impact, root cause in one clause, status of fixes. One document serves
   everyone; this block is what makes that work.
2. **Timeline (facts only)** — every line has a timestamp and a source in
   brackets: `14:02 — error rate hits 18% [Datadog]`. If it can't be sourced,
   it does not go in the timeline; put it in an "Unverified" list at the
   bottom of the section.
3. **Impact** — duration, peak error rate, affected users, failed
   transactions, revenue, support tickets, SLA status.
4. **Root cause** — five-whys chain, terminating at a systemic gap.
5. **Contributing factors** — conditions that made the failure likely.
6. **What went well** — never skip this section.
7. **Action items** — table: Action | Owner | Priority | Due | Addresses.
8. **Follow-up** — a date ~4 weeks out to verify P1 completion, and a
   3-month recurrence check.

## Rules

1. **Blameless means de-personalized causality, not censored facts.** Events
   stay in the timeline with brutal honesty ("deploy pushed to production
   without review [git log]"); what never appears is a person as a *cause*.
   Reframe "who made the mistake" into "what made the mistake likely."
2. **Five whys stop at a system, never at a person.** If a why-chain ends at
   "engineer didn't test enough," keep asking: what would have needed to be
   true in the process for that testing to happen? Root cause is the absent
   process, tool, or document.
3. **Never write "should have."** Assume everyone made the best decision
   available with the information they had at the time.
4. **Missing numbers: state "unknown — needs data from <source>", then give
   an order-of-magnitude estimate labeled as a guess with a confidence level**
   ("likely 1,000–10,000 users affected, low confidence — confirm with
   analytics"). Never silently invent precision; never leave impact blank
   either — a scale-level guess is required so severity can be evaluated.
5. **Ranges, not false precision**, for all impact figures ("$34,000–$41,000").
   Mark every estimate as an estimate.
6. **Action items:** one *named* owner each — never a team; each linked to
   the root cause or a contributing factor it addresses (delete any that
   can't be traced); real priorities — if everything is P1, nothing is;
   concrete due dates.
7. **Disputed facts** between people or teams go in the Unverified list with
   both accounts noted — do not adjudicate in the timeline.

## Process

1. Ingest whatever the user has — notes, Slack dumps, monitoring screenshots,
   memory. Ask for timestamps/sources only for timeline-critical events.
2. Draft all eight sections in order. Where data is missing, apply Rule 4
   rather than stalling.
3. Before presenting, self-check against every rule above; fix violations.
4. If reviewing an existing draft instead of writing one: list violations of
   the rules by section, most severe first, each with the corrected text.
