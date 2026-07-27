"""Skillwise CLI.

Commands:
  skillwise serve [--http] [--port 8321]   Run the MCP server (stdio default)
  skillwise site [--port 8322]             Run the local web UI
  skillwise publish PATH [--author NAME]   Publish a skill folder to the catalog
  skillwise token create NAME              Mint a dev registration token
  skillwise seed                           Publish the bundled sample skills
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import auth, config
from .ingest import IngestError, publish


def _cmd_serve(args) -> None:
    from .server import run
    run(http=args.http, port=args.port)


def _cmd_site(args) -> None:
    import uvicorn
    from .site.app import app
    uvicorn.run(app, host="127.0.0.1", port=args.port)


def _cmd_publish(args) -> None:
    try:
        result = publish(Path(args.path), author_name=args.author)
    except IngestError as exc:
        print(f"REJECTED: {exc}", file=sys.stderr)
        sys.exit(1)
    print(result.message)
    print(f"  sha256: {result.sha256}")
    warnings = [f for f in result.scan["findings"]]
    for f in warnings:
        print(f"  [{f['level']}] {f['check']} — {f['file']}:{f['line']} {f['reason']}")


def _cmd_token(args) -> None:
    if args.action != "create":
        print("Only `token create NAME` is supported.", file=sys.stderr)
        sys.exit(1)
    token = auth.create_token(args.name)
    print(token)
    print("\nConnect Claude Code with:", file=sys.stderr)
    print(f"  claude mcp add skillwise -e SKILLWISE_TOKEN={token} "
          f"-e SKILLWISE_HOME={config.home()} -- skillwise serve", file=sys.stderr)


def _cmd_seed(args) -> None:
    samples = Path(__file__).resolve().parents[2].parent / "examples" / "sample-skills"
    if not samples.is_dir():
        # installed package: look relative to cwd
        samples = config.home() / "examples" / "sample-skills"
    if not samples.is_dir():
        print(f"No sample skills found at {samples}", file=sys.stderr)
        sys.exit(1)
    count = 0
    for skill_dir in sorted(p for p in samples.iterdir() if p.is_dir()):
        try:
            result = publish(skill_dir, author_name="Skillwise Samples")
            print(result.message)
            count += 1
        except IngestError as exc:
            print(f"SKIPPED {skill_dir.name}: {exc}", file=sys.stderr)
    print(f"\nSeeded {count} skill(s) into {config.catalog_dir()}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="skillwise", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("serve", help="Run the MCP server")
    p.add_argument("--http", action="store_true", help="Streamable HTTP instead of stdio")
    p.add_argument("--port", type=int, default=8321)
    p.set_defaults(func=_cmd_serve)

    p = sub.add_parser("site", help="Run the local web UI")
    p.add_argument("--port", type=int, default=8322)
    p.set_defaults(func=_cmd_site)

    p = sub.add_parser("publish", help="Publish a skill folder")
    p.add_argument("path")
    p.add_argument("--author", default="local")
    p.set_defaults(func=_cmd_publish)

    p = sub.add_parser("token", help="Manage dev tokens")
    p.add_argument("action", choices=["create"])
    p.add_argument("name")
    p.set_defaults(func=_cmd_token)

    p = sub.add_parser("seed", help="Publish bundled sample skills")
    p.set_defaults(func=_cmd_seed)

    args = parser.parse_args(argv)
    config.ensure_dirs()
    args.func(args)


if __name__ == "__main__":
    main()
