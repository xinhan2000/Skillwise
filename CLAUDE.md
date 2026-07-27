# Skillwise — project context for Claude Code

Skillwise is an **agent-native marketplace for AI skills, delivered over MCP**.
Agents discover, suggest, and install skills mid-task; every published skill is
security-scanned, hash-pinned, and served through server-side entitlement gating.

- Phase-0 design: `docs/architecture.md` (read before structural changes)
- Phase-1 plan and findings: `docs/phase1-plan.md`
- GitHub: https://github.com/xinhan2000/Skillwise

## Architecture map

```
src/skillwise/
  server.py    MCP server — 7 tools. Anonymous: search_skills, browse_skills,
               get_skill_details, report_gap. Token-gated: install_skill,
               use_skill_now, list_entitlements.
  auth.py      THE auth chokepoint. auth.validate() is the single function that
               swaps to OAuth 2.1 in Phase 1. Entitlement records live here too.
  catalog.py   Index (catalog/catalog.json), package files, canonical sha256
               hashing, weighted search (empty query = browse mode),
               append-only publish log (provenance).
  ingest.py    The ONLY path into the catalog: validate → lint → hash → publish.
  lint.py      8-point static security scan; derives the capabilities manifest.
  events.py    Append-only telemetry (data/events.jsonl).
  cli.py       skillwise serve | site | publish | token | seed
  site/        Local web UI (FastAPI + Jinja), port 8322.
```

## Invariants — do not break these

1. **Published versions are immutable.** New content = new version. Never edit
   a published package or rewrite `catalog/publish_log.jsonl` (append-only).
2. **All catalog writes go through `ingest.publish()`.** No side doors.
3. **Auth checks happen only via `auth.validate()`** (called by
   `server._current_user()`). Don't scatter token logic.
4. **Anonymous reads, gated writes/installs.** search/browse/details/report_gap
   must never require auth; install/use/list must always.
5. **The agent never installs without explicit user approval** — enforced by
   tool descriptions; keep that contract when editing them.
6. **Tool descriptions are product surface.** Changes to them change agent
   behavior; treat like UX changes and test trigger behavior after editing.

## Conventions

- Python 3.10+, no database — JSON files under `SKILLWISE_HOME` (default cwd).
- Run tests as `python -m pytest -q` (avoids conda/venv PATH collisions).
- `pip install -e ".[dev]"` in `.venv`; the venv's absolute binary path is what
  MCP client configs point at.
- `catalog/` and `data/` are generated/runtime — gitignored, never committed.
- CI: `.github/workflows/ci.yml`, Python 3.10 + 3.12, must stay green.

## Key Phase-0 findings (context for Phase-1 choices)

- **Spontaneous mid-task discovery ran ~20%** (bar was 50%): agents don't
  search for capabilities they believe they already have. Discovery works via
  explicit intent; catalog strategy should favor skills with a legible edge
  over model baseline. Full analysis in `docs/phase1-plan.md`.
- **Onboarding stacks three consent layers** (client tool-approval × skillwise
  approval × registration) — friction to design down, not add to.
- **When the MCP server is missing, agents improvise wrong fallbacks**
  (e.g. inventing `claude plugin install` commands) — connector-absent UX matters.
