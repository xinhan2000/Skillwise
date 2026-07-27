# Skillwise — Phase 1 Plan

**Goal:** take the proven local loop to 5–10 external testers on a hosted
server, with real registration — without rewriting anything.
**Principle carried over from Phase 0:** local → remote is configuration and
hardening, not new architecture.

---

## 1. Phase-0 results (July 2026, single-user local testing)

| Test | Result |
|---|---|
| End-to-end loop: discover → approve → gated install → native use | ✅ passed on Claude Code |
| Streaming delivery (`use_skill_now`, no disk) | ✅ passed on Claude Desktop |
| Registration gate (no token → polite refusal + recovery instructions) | ✅ passed |
| Upload → 8-point scan → publish → discoverable | ✅ < 2 min round trip |
| Malicious skill (curl-pipe-bash) blocked at ingest | ✅ rejected with named finding |
| Version immutability + append-only publish log | ✅ (re-upload bumped 1.0.0 → 1.1.0) |
| Bridge delivery (remote agent → desktop-proxied server) | ✅ unplanned third surface |
| **Spontaneous mid-task trigger rate** | ❌ **~20% (1/5), bar was 50%** — held after description tuning |

### The trigger-rate finding (most important learning)

Agents don't search the marketplace for tasks they believe they can do —
and for generic writing/review tasks, they can. The one spontaneous trigger
was a "review"-shaped task (SQL). Implications:

1. **Discovery funnels ranked by expected yield:** explicit intent ("is there
   a skill for X?") > review/procedural task shapes > generic tasks (~0%).
2. **Catalog strategy:** skills that clear the model's baseline in a *legible*
   way (proprietary formats, domain checklists, integrations, company
   workflows) will be discovered and paid for; generic helpers won't.
3. Do not spend more Phase-1 effort tuning descriptions for spontaneous
   triggering; revisit in Phase 3 with data from real users.

### Other findings to design against

- **Consent stack:** client tool-approval + skill-install approval +
  registration = three walls before first value. Mark read-only tools as
  safe/read-only (MCP tool annotations) so clients can auto-approve them.
- **Connector-absent fallback:** with the server missing, the agent invented a
  plausible-but-wrong `claude plugin install` command. Onboarding docs and
  (later) a companion pointer skill should close this.
- Conda/venv PATH collisions and Finder-hidden `/tmp` were real tester
  friction — the Phase-1 README needs a "common macOS gotchas" section.

---

## 2. Phase-1 scope, in priority order

### P0 — Remote deployment of the existing server
- Deploy `skillwise serve --http` (Streamable HTTP, already implemented)
  behind TLS. Suggested host: fly.io or any $5 VPS; SQLite/JSON on a volume
  is fine at this scale.
- `SKILLWISE_HOME` on the server owns the canonical catalog; the local web
  UI becomes the hosted creator UI later (not P0).

### P0 — Real registration: OAuth 2.1
- Swap point is **only** `auth.validate()` (see CLAUDE.md invariant 3).
- MCP spec supports OAuth 2.1 for remote servers: clients detect the auth
  requirement, run the browser flow, attach bearer tokens per call.
- Token → user_id mapping replaces `data/tokens.json`; entitlement records
  keep the same shape. Keep a dev-token mode behind an env flag for tests.

### P1 — Tester onboarding
- One-page connect instructions per client (Claude Code, Claude Desktop,
  Cursor). Include the connector-absent failure mode explicitly.
- Recruit 5–10 testers; each gets the connect URL, no manual token handling.

### P1 — Telemetry as demand data
- events.jsonl moves server-side and gains user attribution automatically.
- Weekly review ritual: no-result searches + gap reports = the build-next
  list; this is the demand-discovery engine from the strategy work.

### P2 — Catalog reseed
- Replace/augment the 5 dev samples with 15–20 curated skills chosen by the
  trigger-rate finding: favor legible-edge skills (formats, integrations,
  domain checklists) over generic helpers.
- Keep provenance: every entry through `ingest.publish()`, log intact.

### Explicitly deferred (Phase 2+)
- Payments/Stripe, entitlement tiers, metered trials on `use_skill_now`.
- Eval/certification pipeline and published scores (the long-term moat).
- Public transparency log; canary fingerprinting on delivery.
- Per-skill licenses (decided direction: source-visible + standardized
  no-redistribution license + platform enforcement — see session notes /
  strategy summary in repo discussions).

---

## 3. Success metrics for Phase 1

1. ≥ 5 external testers connect and complete ≥ 1 gated install each.
2. Onboarding time (URL → first installed skill) under 10 minutes without
   live help.
3. Zero catalog writes that bypass ingest; publish log stays consistent.
4. ≥ 20 telemetry events/week from non-owner users after week 2.
5. At least 3 gap reports or no-result searches that turn into new catalog
   entries — proof the demand loop works.

## 4. Open decisions

1. Hosting target (fly.io vs VPS vs Cloudflare-fronted VPS).
2. OAuth provider: roll our own vs Auth0/WorkOS/Clerk for the browser flow.
3. Whether the hosted web UI ships in Phase 1 (creator uploads) or creators
   go through the owner (curated intake) until Phase 2.
4. Working name check: is "Skillwise" clear for trademark/domain before any
   public tester sees it?
