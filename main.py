from __future__ import annotations

import hmac
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

BASE_DIR = Path(__file__).resolve().parent
BOTS_DIR = BASE_DIR / "bots"
BOTS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Zentry-Code | Faxriddin Baxodirov", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "zentry-super-secret-key-2026"),
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
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/ping")
async def ping():
    return {"status": "ok", "service": "zentry-code"}


@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    if not request.session.get("admin_authenticated"):
        return templates.TemplateResponse(request=request, name="admin.html", context={"login": True, "error": None})
    
    bot_files = [f.name for f in BOTS_DIR.glob("*.py")]
    selected_bot = request.query_params.get("bot", bot_files[0] if bot_files else "")
    
    code_content = ""
    if selected_bot and (BOTS_DIR / selected_bot).exists():
        code_content = (BOTS_DIR / selected_bot).read_text(encoding="utf-8")

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "login": False,
            "error": None,
            "bot_files": bot_files,
            "selected_bot": selected_bot,
            "code": code_content,
            "output": None
        }
    )


@app.post("/admin/login")
async def admin_login(request: Request):
    configured_password = os.getenv("ADMIN_PASSWORD", "zentry2026")
    raw_form = (await request.body()).decode("utf-8", errors="replace")
    supplied_password = parse_qs(raw_form).get("password", [""])[0]
    
    if not hmac.compare_digest(supplied_password, configured_password):
        return templates.TemplateResponse(
            request=request,
            name="admin.html",
            context={"login": True, "error": "Parol noto‘g‘ri."},
            status_code=401,
        )

    request.session.clear()
    request.session["admin_authenticated"] = True
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/bot/create")
async def admin_create_bot(request: Request):
    if not request.session.get("admin_authenticated"):
        return RedirectResponse("/admin", status_code=303)
    
    raw_form = (await request.body()).decode("utf-8", errors="replace")
    parsed = parse_qs(raw_form)
    bot_name = parsed.get("bot_name", [""])[0].strip()
    
    if bot_name:
        if not bot_name.endswith(".py"):
            bot_name += ".py"
        bot_path = BOTS_DIR / bot_name
        if not bot_path.exists():
            bot_path.write_text("# Yangi bot yoki skript\nprint('Zentry-Code bot ishga tushdi!')\n", encoding="utf-8")
            
    return RedirectResponse(f"/admin?bot={bot_name}", status_code=303)


@app.post("/admin/bot/save")
async def admin_save_bot(request: Request):
    if not request.session.get("admin_authenticated"):
        return RedirectResponse("/admin", status_code=303)
    
    raw_form = (await request.body()).decode("utf-8", errors="replace")
    parsed = parse_qs(raw_form)
    bot_name = parsed.get("bot_name", [""])[0]
    code = parsed.get("code", [""])[0]
    
    if bot_name:
        bot_path = BOTS_DIR / bot_name
        bot_path.write_text(code, encoding="utf-8")
        
    return RedirectResponse(f"/admin?bot={bot_name}", status_code=303)


@app.post("/admin/bot/run")
async def admin_run_bot(request: Request):
    if not request.session.get("admin_authenticated"):
        return RedirectResponse("/admin", status_code=303)
    
    raw_form = (await request.body()).decode("utf-8", errors="replace")
    parsed = parse_qs(raw_form)
    bot_name = parsed.get("bot_name", [""])[0]
    
    output = "Xatolik: Bot topilmadi."
    if bot_name:
        bot_path = BOTS_DIR / bot_name
        if bot_path.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(bot_path)],
                    capture_output=True,
                    text=True,
                    timeout=20,
                    cwd=str(BASE_DIR)
                )
                output = result.stdout if result.stdout else ""
                if result.stderr:
                    output += f"\n[XATOLIK / STDERR]:\n{result.stderr}"
                if not output.strip():
                    output = "// Bot muvaffaqiyatli bajarildi (natija bo'sh)."
            except Exception as e:
                output = f"Ijro etish xatoligi: {str(e)}"

    bot_files = [f.name for f in BOTS_DIR.glob("*.py")]
    code_content = (BOTS_DIR / selected_bot).read_text(encoding="utf-8") if (selected_bot := bot_name) and (BOTS_DIR / bot_name).exists() else ""

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "login": False,
            "error": None,
            "bot_files": bot_files,
            "selected_bot": bot_name,
            "code": code_content,
            "output": output
        }
    )


@app.post("/admin/shell")
async def admin_shell(request: Request):
    if not request.session.get("admin_authenticated"):
        return RedirectResponse("/admin", status_code=303)
    
    raw_form = (await request.body()).decode("utf-8", errors="replace")
    parsed = parse_qs(raw_form)
    cmd = parsed.get("cmd", [""])[0].strip()
    selected_bot = parsed.get("selected_bot", [""])[0]
    
    output = f"$ {cmd}\n"
    if cmd:
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=40,
                cwd=str(BASE_DIR)
            )
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\n{result.stderr}"
            if not result.stdout and not result.stderr:
                output += "// Buyruq bajarildi (natija qaytmadi)."
        except Exception as e:
            output += f"\nXatolik: {str(e)}"
    else:
        output += "Buyruq kiritilmadi."

    bot_files = [f.name for f in BOTS_DIR.glob("*.py")]
    code_content = (BOTS_DIR / selected_bot).read_text(encoding="utf-8") if selected_bot and (BOTS_DIR / selected_bot).exists() else ""

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "login": False,
            "error": None,
            "bot_files": bot_files,
            "selected_bot": selected_bot,
            "code": code_content,
            "output": output
        }
    )


@app.post("/admin/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin", status_code=303)
