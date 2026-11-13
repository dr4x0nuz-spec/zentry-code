# Zentry-Code — shaxsiy portfolio

Faxriddin Baxodirov (`Zentry404`) uchun FastAPI asosidagi, mobil qurilmalarga mos shaxsiy sahifa.

## Lokal ishga tushirish

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Sayt `http://127.0.0.1:8000` manzilida, holat tekshiruvi esa `/ping` va `/healthz` yo‘llarida ishlaydi.

## Render’da joylash

1. GitHub repozitoriyni Render’ga ulang va `render.yaml` blueprint sozlamalaridan foydalaning.
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Render Environment’da kuchli `ADMIN_PASSWORD` belgilang. `SESSION_SECRET` uchun uzun, tasodifiy qiymat ishlating (Blueprint uni o‘zi yaratadi).
5. UptimeRobot monitor URL: `https://<render-domeningiz>/ping`.

**Bepul tarif bo‘yicha eslatma:** Render Free web service nofaol davrdan keyin uxlab qolishi mumkin; tashqi ping uyg‘otishga yordam berishi mumkin, ammo 24/7 ishlash kafolati emas. DuckDNS domen ulanishi ham Render konfiguratsiyasi va DNS sozlamalariga bog‘liq. UptimeRobot ping’i uptime kafolatlamaydi.

## Admin va xavfsizlik

`/admin` faqat `ADMIN_PASSWORD` bilan kiriladigan kichik, sessiyali boshqaruv sahifasidir. Ixtiyoriy Python kodini yoki botlarni web so‘rovi orqali serverda ishga tushiradigan umumiy kod bajarish funksiyasi ataylab kiritilmagan: bunday runner server egasining o‘ziga ham xavf tug‘diradi va Render Free doimiy background jarayonlarga mos emas. Botlarni alohida, ishonchli worker/hosting’da joylashtiring.

## Logo va favicon

`static/logo.svg` va `static/favicon.svg` — namunaviy vektor emblemalar. O‘zingizning rasm logotipingizni qo‘shmoqchi bo‘lsangiz, `templates/index.html` ichidagi logo manzillarini o‘zingiz yuklagan faylga almashtiring. SVG favicon barcha zamonaviy brauzerlarda ishlaydi; `/favicon.ico` ham unga yo‘naltiradi.
