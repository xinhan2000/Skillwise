# Skillwise

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

Seven MCP tools: `search_skills`, `browse_skills`, `get_skill_details`,
`report_gap` (anonymous) and `install_skill`, `use_skill_now`,
`list_entitlements` (registered users only). `use_skill_now` streams a skill
straight into context without touching disk — the seed of metered delivery.

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

## User CLI

The same marketplace, driven from a terminal (or by an agent running shell
commands). Reads are anonymous; the first `add` prompts once to register and
stores the token in `~/.skillwise/config.json`.

```bash
skillwise search [query]     # no query = browse the whole catalog
skillwise add <skill-id>     # confirm, register once, install (-y to skip prompts)
skillwise list               # what's installed via Skillwise, active or paused
skillwise pause <skill-id>   # disable without uninstalling (moves to skills-paused/)
skillwise resume <skill-id>  # re-enable
skillwise remove <skill-id>  # uninstall
skillwise login              # (re)register this machine
```

The CLI talks through a dual-backend client (`client.py`): in-process against
the local catalog today, or over the REST API (`/api/*`, served by the site
app) when `server_url` is set in `~/.skillwise/config.json` — the Phase-1
hosted mode. Install target defaults to `~/.claude/skills` (override with
`install_dir` in the config). Non-interactive shells get actionable errors
(e.g. "re-run with -y") instead of prompts.

## Repo layout

```
src/skillwise/          the package
  server.py             MCP server (7 tools, stdio + streamable-http)
  cli.py                CLI entry (operator + user subcommands)
  user_cli.py           user commands: search/list/add/pause/resume/remove/login
  client.py             dual-backend client: in-process local or REST (HttpBackend)
  userstate.py          ~/.skillwise config + installed-skill manifest
  ingest.py             validate → lint → hash → publish pipeline
  lint.py               8-point security scan
  catalog.py            index, packages, hashing, search, publish log
  auth.py               dev-token auth (Phase-1: OAuth 2.1) + entitlements
  events.py             append-only telemetry (searches, installs, gaps)
  site/                 local web UI + REST API /api/* (FastAPI + Jinja)
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
