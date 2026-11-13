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
                # Popen orqali fonda (background) ishga tushiramiz, u vaqt cheklovisiz 24/7 ishlaydi
                process = subprocess.Popen(
                    [sys.executable, str(bot_path)],
                    cwd=str(BASE_DIR),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                output = f"// Bot ({bot_name}) fonda muvaffaqiyatli ishga tushirildi! (Process ID: {process.pid})\n// Endi u 24/7 ishlaydi."
            except Exception as e:
                output = f"Ijro etish xatoligi: {str(e)}"

    bot_files = [f.name for f in BOTS_DIR.glob("*.py")]
    code_content = (BOTS_DIR / bot_name).read_text(encoding="utf-8") if (BOTS_DIR / bot_name).exists() else ""

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
