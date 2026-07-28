"""End-user CLI commands: search, list, add, pause, resume, remove, login.

Sign-in happens only when necessary: search/list/pause/resume/remove are
anonymous or purely local; `add` prompts once and stores the token in
~/.skillwise/config.json.
"""

from __future__ import annotations

import shutil
import sys

from . import userstate
from .client import ClientError, RegistrationRequired, get_backend


def _fail(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def _prompt(text: str) -> str | None:
    """input() that survives non-interactive shells: returns None on EOF."""
    try:
        return input(text)
    except EOFError:
        return None


def _print_results(results: list[dict]) -> None:
    if not results:
        print("No skills found.")
        return
    installed = userstate.load_manifest()
    for r in results:
        caps = r.get("capabilities", {})
        cap_note = " ".join(k for k, v in caps.items() if v) or "no special access"
        price = "free" if not r.get("price_usd") else f"${r['price_usd']}"
        mark = ""
        if r["id"] in installed:
            mark = " [installed, paused]" if installed[r["id"]].get("paused") else " [installed]"
        print(f"  {r['id']}  v{r['version']}  {price}  scan:{r.get('scan_status', '?')}  "
              f"({cap_note}){mark}")
        print(f"      {r.get('one_liner', '')[:100]}")


def _ensure_token(cfg: dict, backend) -> str:
    """Prompt-once registration: only called by commands that need auth."""
    if cfg.get("token"):
        return cfg["token"]
    print("Installing requires a (free) Skillwise account — one-time setup.")
    name = _prompt("Your name or handle: ")
    if name is None:
        _fail("registration needs an interactive terminal — run `skillwise login` there once, "
              "then non-interactive installs will work")
    name = name.strip()
    if not name:
        _fail("registration cancelled (empty name)")
    token = backend.register(name)
    cfg["token"] = token
    cfg["user_name"] = name
    userstate.save_config(cfg)
    print(f"Registered as {name!r}. Token stored in {userstate.user_dir()}/config.json\n")
    return token


def cmd_search(args) -> None:
    cfg = userstate.load_config()
    try:
        backend = get_backend(cfg)
        results = backend.search(args.query or "", limit=args.limit)
    except ClientError as exc:
        _fail(str(exc))
    _print_results(results)


def cmd_list(args) -> None:
    manifest = userstate.load_manifest()
    if not manifest:
        print("No skills installed via Skillwise.")
        return
    for skill_id, info in sorted(manifest.items()):
        status = "paused" if info.get("paused") else "active"
        print(f"  {skill_id}  v{info['version']}  [{status}]  installed {info['installed_at']}")


def cmd_add(args) -> None:
    cfg = userstate.load_config()
    try:
        backend = get_backend(cfg)
    except ClientError as exc:
        _fail(str(exc))

    entry = backend.get(args.skill_id)
    if entry is None:
        print(f"No skill {args.skill_id!r}. Closest matches:")
        _print_results(backend.search(args.skill_id.replace("-", " "), limit=3))
        sys.exit(1)

    scan = entry.get("scan", {}).get("status", entry.get("scan_status", "?"))
    caps = entry.get("capabilities", {})
    cap_note = ", ".join(k for k, v in caps.items() if v) or "no network/shell/file access"
    print(f"{entry['name']} v{entry['version']} — scan: {scan} — {cap_note}")
    if not args.yes:
        answer = _prompt("Install? [y/N] ")
        if answer is None:
            _fail("no interactive terminal to confirm — re-run with -y/--yes "
                  f"(e.g. `skillwise add {args.skill_id} -y`)")
        if answer.strip().lower() not in ("y", "yes"):
            print("Cancelled.")
            return

    token = _ensure_token(cfg, backend)
    try:
        result = backend.install(args.skill_id, token)
    except RegistrationRequired as exc:
        _fail(f"registration problem: {exc}")
    except ClientError as exc:
        _fail(str(exc))

    target = userstate.install_dir(cfg) / args.skill_id
    if target.exists():
        shutil.rmtree(target)
    for rel, content in result["files"].items():
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    userstate.record_install(args.skill_id, result["version"], result["sha256"])
    print(f"Installed {args.skill_id} v{result['version']} → {target}")
    print("New agent sessions will pick it up automatically.")


def cmd_pause(args) -> None:
    cfg = userstate.load_config()
    src = userstate.install_dir(cfg) / args.skill_id
    dst = userstate.paused_dir(cfg) / args.skill_id
    manifest = userstate.load_manifest()
    if args.skill_id not in manifest:
        _fail(f"{args.skill_id!r} is not managed by Skillwise (see `skillwise list`)")
    if manifest[args.skill_id].get("paused"):
        print(f"{args.skill_id} is already paused.")
        return
    if not src.exists():
        _fail(f"expected skill folder missing: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    userstate.set_paused(args.skill_id, True)
    print(f"Paused {args.skill_id} (moved to {dst.parent}). `skillwise resume {args.skill_id}` to re-enable.")


def cmd_resume(args) -> None:
    cfg = userstate.load_config()
    src = userstate.paused_dir(cfg) / args.skill_id
    dst = userstate.install_dir(cfg) / args.skill_id
    manifest = userstate.load_manifest()
    if args.skill_id not in manifest:
        _fail(f"{args.skill_id!r} is not managed by Skillwise")
    if not manifest[args.skill_id].get("paused"):
        print(f"{args.skill_id} is not paused.")
        return
    if not src.exists():
        _fail(f"expected paused folder missing: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    userstate.set_paused(args.skill_id, False)
    print(f"Resumed {args.skill_id}.")


def cmd_remove(args) -> None:
    cfg = userstate.load_config()
    manifest = userstate.load_manifest()
    if args.skill_id not in manifest:
        _fail(f"{args.skill_id!r} is not managed by Skillwise (see `skillwise list`)")
    removed = False
    for base in (userstate.install_dir(cfg), userstate.paused_dir(cfg)):
        folder = base / args.skill_id
        if folder.exists():
            shutil.rmtree(folder)
            removed = True
    userstate.remove_record(args.skill_id)
    print(f"Removed {args.skill_id}." + ("" if removed else " (no files found; record cleared)"))


def cmd_login(args) -> None:
    cfg = userstate.load_config()
    try:
        backend = get_backend(cfg)
    except ClientError as exc:
        _fail(str(exc))
    cfg.pop("token", None)
    _ensure_token(cfg, backend)
