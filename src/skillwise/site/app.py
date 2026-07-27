"""Skillwise local web UI: browse, detail, upload."""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

from fastapi import Body, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .. import catalog, config
from ..client import ClientError, LocalBackend, RegistrationRequired
from ..ingest import IngestError, publish

app = FastAPI(title="Skillwise")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


# ---------- REST API (used by HttpBackend / future hosted clients) ----------

@app.get("/api/skills")
def api_search(q: str = "", limit: int = 20):
    return {"results": LocalBackend().search(q, limit=limit)}


@app.get("/api/skills/{skill_id}")
def api_get(skill_id: str):
    entry = catalog.get_entry(skill_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"No skill {skill_id!r}")
    return entry


@app.post("/api/register")
def api_register(body: dict = Body(...)):
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    return {"token": LocalBackend().register(name)}


@app.post("/api/skills/{skill_id}/install")
def api_install(skill_id: str, authorization: str | None = Header(default=None)):
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:]
    try:
        return LocalBackend().install(skill_id, token)
    except RegistrationRequired as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except ClientError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/", response_class=HTMLResponse)
def index(request: Request, q: str = ""):
    entries = catalog.search(q, limit=50) if q else catalog.load_index()
    return templates.TemplateResponse(request, "index.html", {
        "entries": entries, "q": q, "count": len(catalog.load_index()),
    })


@app.get("/skill/{skill_id}", response_class=HTMLResponse)
def detail(request: Request, skill_id: str):
    entry = catalog.get_entry(skill_id)
    if entry is None:
        return HTMLResponse(f"<h1>Not found: {skill_id}</h1>", status_code=404)
    files = catalog.package_files(skill_id, entry["version"])
    return templates.TemplateResponse(request, "detail.html", {
        "e": entry, "files": sorted(files.keys()),
        "skill_md": files.get("SKILL.md", ""),
    })


@app.get("/upload", response_class=HTMLResponse)
def upload_form(request: Request):
    return templates.TemplateResponse(request, "upload.html", {"result": None, "error": None})


@app.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, package: UploadFile = File(...), author: str = Form("local")):
    result = error = None
    tmp = Path(tempfile.mkdtemp(prefix="skillwise-upload-"))
    try:
        zip_path = tmp / "package.zip"
        zip_path.write_bytes(await package.read())
        extract_dir = tmp / "package"
        with zipfile.ZipFile(zip_path) as zf:
            for name in zf.namelist():
                if name.startswith("/") or ".." in name:
                    raise IngestError(f"Unsafe path in zip: {name}")
            zf.extractall(extract_dir)
        # allow zips that wrap everything in a single top-level folder
        root = extract_dir
        children = [p for p in extract_dir.iterdir() if not p.name.startswith("__MACOSX")]
        if len(children) == 1 and children[0].is_dir():
            root = children[0]
        result = publish(root, author_name=author)
    except (IngestError, zipfile.BadZipFile) as exc:
        error = str(exc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return templates.TemplateResponse(request, "upload.html", {"result": result, "error": error})
