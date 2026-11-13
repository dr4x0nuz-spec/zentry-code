from __future__ import annotations

import hmac
import os
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Zentry-Code | Faxriddin Baxodirov", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Set SESSION_SECRET to a long, random value in Render. The fallback is suitable for
# local preview only; sessions will be invalidated if the process restarts.
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "local-preview-change-this-secret"),
    session_cookie="zentry_session",
    same_site="lax",
    https_only=os.getenv("RENDER", "").lower() == "true",
    max_age=60 * 60 * 12,
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith("/admin"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/ping")
async def ping():
    return {"status": "ok", "service": "zentry-code"}


@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    if request.session.get("admin_authenticated"):
        return templates.TemplateResponse(
            "admin.html", {"request": request, "error": None}
        )
    return templates.TemplateResponse(
        "admin.html", {"request": request, "error": None, "login": True}
    )


@app.post("/admin/login")
async def admin_login(request: Request):
    configured_password = os.getenv("ADMIN_PASSWORD")
    if not configured_password:
        raise HTTPException(status_code=503, detail="Admin panel is not configured")

    raw_form = (await request.body()).decode("utf-8", errors="replace")
    supplied_password = parse_qs(raw_form).get("password", [""])[0]
    if not hmac.compare_digest(supplied_password, configured_password):
        return templates.TemplateResponse(
            "admin.html",
            {"request": request, "error": "Parol noto‘g‘ri.", "login": True},
            status_code=401,
        )

    request.session.clear()
    request.session["admin_authenticated"] = True
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin", status_code=303)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse("/static/favicon.svg", status_code=307)


@app.get("/healthz", include_in_schema=False)
async def healthz():
    return Response(content="ok", media_type="text/plain")
