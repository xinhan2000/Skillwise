# Skillwise

[![CI](https://github.com/xinhan2000/Skillwise/actions/workflows/ci.yml/badge.svg)](https://github.com/xinhan2000/Skillwise/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**An agent-native marketplace for AI skills, delivered over MCP.**

Skillwise lets any MCP-capable agent (Claude Code, Claude Desktop, Cursor, …) discover,
suggest, and install skills mid-task — with a security scan on every published skill,
server-side registration gating, and provenance hashing from day one.

> Phase 0: fully local MVP. One machine, one user, zero cloud dependencies.
> See [`docs/architecture.md`](docs/architecture.md) for the full design.

## How it works

```
User: "Turn this order list into a proper invoice PDF"
  → Agent calls search_skills("invoice pdf")          (anonymous)
  → Skillwise returns a scanned, hash-pinned match
  → Agent asks the user for approval                  (always)
  → Agent calls install_skill(...)                    (requires token)
  → Files land in ~/.claude/skills/… — task continues
```

Six MCP tools: `search_skills`, `get_skill_details`, `report_gap` (anonymous) and
`install_skill`, `use_skill_now`, `list_entitlements` (registered users only).
`use_skill_now` streams a skill straight into context without touching disk —
the seed of metered delivery.

## Quickstart

```bash
git clone <this repo> && cd skillwise
pip install -e ".[dev]"

# 1. Publish the bundled sample skills into your local catalog
skillwise seed

# 2. Register (Phase-0 dev token; OAuth 2.1 arrives with the hosted version)
skillwise token create yourname
# → prints swk_… and the exact `claude mcp add` command to run

# 3. Connect Claude Code (stdio)
claude mcp add skillwise \
  -e SKILLWISE_TOKEN=swk_yourtoken \
  -e SKILLWISE_HOME=/absolute/path/to/skillwise \
  -- skillwise serve

# 4. Browse / upload skills in a browser
skillwise site        # http://localhost:8322
```

Then ask Claude for something a catalog skill covers ("review this SQL query")
and watch it discover, suggest, and — with your approval — install the skill.

## Publishing a skill

A skill is a folder with a `SKILL.md` (YAML frontmatter: `name`, `description`,
optional `tags`) plus any supporting files.

```bash
skillwise publish path/to/my-skill --author "Your Name"
```

Every upload runs the **8-point security lint** (dangerous shell, network access,
credential harvesting, hardcoded secrets, obfuscation, prompt injection,
filesystem escape, binary payloads). Hard findings block publication; warnings
publish but are displayed on the listing and in pre-install summaries. Every
version is immutable, sha256-hashed, and appended to `catalog/publish_log.jsonl`
— the provenance record.

## Repo layout

```
src/skillwise/          the package
  server.py             MCP server (6 tools, stdio + streamable-http)
  cli.py                skillwise CLI (serve | site | publish | token | seed)
  ingest.py             validate → lint → hash → publish pipeline
  lint.py               8-point security scan
  catalog.py            index, packages, hashing, search, publish log
  auth.py               dev-token auth (Phase-1: OAuth 2.1) + entitlements
  events.py             append-only telemetry (searches, installs, gaps)
  site/                 local web UI (FastAPI + Jinja)
examples/sample-skills/ 5 skills for the dev catalog
tests/                  pytest suite
docs/architecture.md    Phase-0 design document
```

Runtime data stays out of git: `catalog/` is generated (`skillwise seed`) and
`data/` holds tokens/telemetry (see `.gitignore`).

## Roadmap

- **Phase 0 (this repo):** local MVP — agent-native discovery, gated installs, scan pipeline.
- **Phase 1:** deploy the same server remotely (Streamable HTTP), real OAuth 2.1, external testers.
- **Phase 2:** payments, entitlement tiers, metered trials on `use_skill_now`.
- **Phase 3:** eval/certification pipeline with published scores, public transparency log, creator dashboard.

## Development

```bash
pip install -e ".[dev]"
pytest -v
```

## License

MIT — see [LICENSE](LICENSE). (Skills published to a future hosted Skillwise
carry their own per-skill licenses.)
