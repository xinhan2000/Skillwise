# Skillwise — Strategy fork: 2C marketplace vs 2B platform vs both

**Date:** 2026-07-28 · **Status:** Decided — build the common core first, then
run the fork as a parallel market test with a pre-committed decision rule.

## 1. The question

With the full local product working (marketplace server, user CLI, creator
pipeline with eval gates), where does Skillwise point next:

- **Option 1 — 2C:** open marketplace; anyone creates, shares, sells skills.
- **Option 2 — 2B:** enterprise skill-management platform (private, audited,
  governed skill registries per company).
- **Option 3 — both.**

## 2. Evidence base (accumulated this project)

- **2C economics are empirically thin.** Agensi (closest comp): median paid
  skill earns <$50/month; ~2,000 skills vs ~3,000 users (supply-heavy).
  GPT Store: monetization failed at consumer scale.
- **Enterprise demand is documented in the market's own words.** Glama's
  ecosystem report: enterprises requesting "private registries of audited
  and allow-listed" components. Nobody serves this for the Claude skill
  ecosystem.
- **Our Phase-0/EXP findings weaken the 2C funnel:** ~20% spontaneous
  trigger rate (confirmed cross-surface), plus trigger competition from
  users' installed plugins (observed live: a popular plugin shadowed our
  create-skill until intent was made explicit). 2C growth fights discovery
  physics; 2B admins curate, so it mostly doesn't.
- **Platform risk is asymmetric.** An official Anthropic store would flatten
  an open 2C marketplace; it would NOT manage a company's private skills.
- **What we built maps to 2B almost 1:1:** gated installs → access control;
  scan + provenance + evals + immutable versions + publish log → compliance
  story; create-skill → "turn tribal knowledge into managed skills."

## 3. Evaluation summary

| | 2C marketplace | 2B platform | Both now |
|---|---|---|---|
| Willingness to pay | Thin (evidence above) | Real, documented | — |
| Cold start | Two-sided, hardest | One-sided (supply is internal) | Double |
| Growth motion | Self-serve, viral upside | Sales-led, slow, founder-heavy | Two motions |
| Discovery risk | High (trigger findings) | Low (admin curation) | — |
| Platform risk | Maximal | Lowest | — |
| Feature tax | Moderation, IP policing | SSO/SAML, RBAC, audit, SOC2 | Both taxes |
| Fit to what's built | Good | Near 1:1 | — |
| Solo-founder feasibility | OK | Hard but focused | **Disqualifying** |

Option 3's honest form is **sequencing, not parallelism** — two GTMs at MVP
stage means neither done well.

## 4. The common denominator (~80% of the build is shared)

**Build-anyway core (Phase 1):**

1. **Hosted multi-tenant server** — deploy the existing server over
   Streamable HTTP; OAuth 2.1; one account across MCP/CLI/web (already P0).
2. **Catalogs as first-class tenants** ← the one NEW architectural
   requirement from this decision. Public marketplace = one catalog; each
   enterprise = a private catalog; dev = another. Identical machinery,
   different config — same pattern as the CLI's Local/Http dual backend.
   Build the abstraction now so 2C-vs-2B is configuration, not rewrite.
3. **Entitlement/visibility layer** — one ACL mechanism serves both
   "paid skill visible to buyers" (2C) and "private skill visible to org
   members" (2B). Monetization and privacy are the same primitive.
4. **Trust pipeline** (exists): scan, provenance, eval blocks, immutable
   versions, append-only publish log — 2C differentiation and 2B compliance
   from one codebase. Surface it in the UI.
5. **Creator pipeline** (exists): identical for public creators and internal
   experts.
6. **Web UI** over the existing REST API: catalog browse, listing pages that
   display scan/eval/provenance, draft review.
7. **Telemetry** (exists): same events become 2C ranking/creator dashboards
   and 2B admin usage reports.

**Genuinely divergent — defer until the fork is decided:**
Stripe checkout + rev share (2C only); SSO/SAML, RBAC, audit exports, admin
console (2B only); discovery algorithms and social features (2C only).
Identity is core; billing is not.

## 5. Decision

1. **Build the common core as Phase 1** (existing plan + tenancy). Est. 2–4
   focused weeks.
2. **Then run both tests cheaply in parallel:**
   - *2C-lite:* launch the public catalog **free** (no payments) — it is
     marketing, demo, and community front porch; sidesteps the thin-economics
     trap entirely. Measure organic creators and installs not manufactured
     by us.
   - *2B probe:* five design-partner conversations with companies, using the
     live product as the demo ("your team's private, audited skill registry").
3. **Pre-committed decision rule:** if design partners convert or lean in
   hard → focus 2B, keep 2C as the free funnel. If 2B stalls AND the public
   catalog shows real organic creator pull → revisit. Working prior: ~70/30
   the revenue is Option 2 with 2C as its marketing layer.
4. Being wrong costs a configuration change, not a rebuild — that is the
   point of the core-first sequencing.

## 6. Immediate implications

- Phase-1 plan amended: tenancy/catalog abstraction added to P0 scope
  (see `phase1-plan.md`).
- No Stripe work, no SSO work, no discovery-algorithm work until the fork
  is decided.
- The mcp<2 pin stays until a scheduled SDK migration (lockfile discipline
  when the hosted server deploys).
