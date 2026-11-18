# student_bot

Telegram bot: istalgan matnni yuboring — bot uni xuddi qo'lda yozilgandek,
ko'k siyohda, daftar varag'i fonida konspekt rasmiga aylantirib beradi.

## Qanday ishlaydi

- `handwriting/` — rasm generatsiya qiluvchi "mexanizm" (Pillow asosida):
  - `paper.py` — chiziqli/katakli daftar foni, qizil chekka chizig'i, qog'oz
    teksturasi va foto-effektlar (nozik egilish, shovqin, xiralik).
  - `textshape.py` — matnni sarlavha (`# ...`), ro'yxat (`- ...`) va abzatslarga
    ajratadi, so'zlarni qatorlarga bo'ladi.
  - `render.py` — har bir harfni alohida, tasodifiy burilish/joylashuv/oraliq
    bilan chizadi (shuning uchun shrift emas, qo'lda yozilgandek ko'rinadi),
    sahifalarga bo'lib chiqadi.
  - `style.py` — tayyor uslublar (shrift + qog'oz turi + siyoh rangi).
- `bot.py`, `handlers.py`, `keyboards.py` — aiogram 3 asosidagi Telegram bot
  qatlami: matnni qabul qiladi, uslub tanlash tugmalarini chiqaradi, rasmlarni
  (ko'p sahifali bo'lsa albom qilib) jo'natadi.

## O'rnatish

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # BOT_TOKEN ni @BotFather dan olib qo'ying
```

## Ishga tushirish (lokal, polling)

```bash
source .venv/bin/activate
python bot.py
```

## Render.com'da deploy qilish

Loyihani **Background Worker** sifatida joylashtiring (webhook kerak emas,
bot `polling` rejimida ishlaydi):

- Build command: `pip install -r requirements.txt`
- Start command: `python bot.py`
- Environment variable: `BOT_TOKEN` (`@BotFather`'dan olingan token)

## Yangi yozuv uslubi qo'shish

`handwriting/style.py` ichidagi `STYLES` lug'atiga yangi `HandwritingStyle`
qo'shing (shrift fayli `handwriting/fonts/` papkasida bo'lishi kerak) — u
avtomatik ravishda `/uslub` tugmalar ro'yxatida paydo bo'ladi.
