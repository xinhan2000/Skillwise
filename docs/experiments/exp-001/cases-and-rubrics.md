# EXP-001 — Eval cases and rubrics

Shared rubric (binary, scored per case unless marked N/A):
- R1 Summary block at top (≤5 lines; impact + cause + fix status)
- R2 Timeline: every entry timestamped AND sourced; unsourced facts moved to an Unverified list
- R3 Blameless: no person named as a cause anywhere; zero "should have" phrasing
- R4 Root cause is systemic (process/tool/doc gap), reached via a visible why-chain; not "human error"
- R5 "What went well" section present and non-empty
- R6 Action items: named individual owners (no teams), linked to cause/factor, mixed priorities, due dates
- R7 Missing data handled per rule: "unknown — needs data from <src>" PLUS order-of-magnitude guess with confidence label
- R8 Impact figures as ranges; estimates marked as estimates
- R9 Follow-up section with ~4-week P1 check (and/or 3-month recurrence check)
- R10 Case-specific item (below)

---

## Case 1 — WRITE, article-derived (checkout N+1)

Input notes:
"Friday peak traffic. ~14:00 checkout started timing out. Datadog showed DB
connections maxed. 14:02 error rate 18% (datadog). Deploy of checkout-service
v2.4.1 went out 13:47 (git). Rolled back 14:11, recovered 14:14ish. Support
got a bunch of tickets. Maybe 8-9k users hit? Finance thinks we lost
somewhere around 34-41k in failed checkouts. Turned out v2.4.1 introduced an
N+1 query. Connection pool was max 20, nobody knew who set that or why. Our
load tests didn't catch it - staging traffic looks nothing like prod."

R10: root cause lands on a systemic gap (pool-sizing documentation absent /
load-test fidelity), consistent with the facts, not "bad deploy."

## Case 2 — REVIEW mode, article-derived ("before" postmortem)

Input: "Review this postmortem draft:
'Root cause: Database performance degradation caused by increased load.
Actions: improve database monitoring; review deploy process; add more tests.
The incident lasted 14 minutes and affected checkout.'"

R10: review flags (a) root cause is a symptom, why-chain missing; (b) action
items vague, unowned, unlinked, unprioritized, undated; (c) missing sections
(timeline, impact quantification, what-went-well, follow-up). Corrected text
offered for at least the action items.

## Case 3 — TRAP: blame bait

Input notes:
"Tuesday. 09:12 alerts fire, API 5xx spiking (pagerduty). Dave force-pushed a
config change straight to prod at 09:05 without review - AGAIN, classic Dave.
09:30 rolled back (git), recovery 09:33 (datadog). ~45 min of elevated errors
for EU customers, maybe 2% of requests. Dave says the staging config drifted
so testing there was useless. Also our config pipeline has no validation step
and honestly review is optional for config repos."

R10: the force-push FACT stays in the timeline (timestamped, sourced,
person-neutral or role-neutral phrasing acceptable), Dave is never the CAUSE;
root cause lands on config pipeline validation/review-optionality; the
"AGAIN, classic Dave" editorializing is dropped.

## Case 4 — TRAP: missing data + hindsight bait

Input notes:
"we had an outage yesterday evening, search was down or flaky for a while,
started sometime after the 18:00 index rebuild kicked off, fixed by
restarting the cluster around 19:30. no idea how many users noticed. we
obviously should have caught this in the rebuild runbook, it's happened
twice before. es cluster ran out of heap during rebuild. no monitoring on
heap for that cluster."

R10: impact section says unknown + needs-data source AND gives a labeled
order-of-magnitude guess with confidence; "should have" bait does not appear
in output; recurrence (twice before) surfaces in root cause/contributing
factors as a systemic follow-up gap.

## Case 5 — TRAP: multi-team disputed facts

Input notes:
"Payments degraded 11:20-12:05 Thu (statuspage). Payments team says platform
silenced the relevant alert during maintenance and never unsilenced it.
Platform team says the alert was never configured for the new gateway and
payments knew. Nobody can find the silence in the alerting audit log yet.
Gateway migration happened 2 weeks ago. Failover to backup provider worked
at 11:58 (payments oncall). Revenue impact unclear, maybe five figures."

R10: the silenced-vs-never-configured dispute goes to Unverified with both
accounts recorded, NOT adjudicated in the timeline; root cause work proceeds
on what's known (alert coverage gap for migrated gateway, audit-log
verification as action item).

## Case 6 — EDGE: no customer impact

Input notes:
"CI was down all Wednesday morning, runners kept OOMing after the docker
upgrade tuesday night. devs couldn't merge for ~4 hours. zero customer
impact. fixed by pinning runner image and doubling runner memory. write me
a postmortem?"

R10: recognizes no customer impact → says a full postmortem isn't warranted
under the threshold and offers/produces the lightweight form (timeline +
action items) instead of the full 8 sections.
