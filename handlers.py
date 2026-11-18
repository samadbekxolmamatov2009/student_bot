import asyncio
import io
import random

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, CallbackQuery, InputMediaPhoto, Message

from config import MAX_PAGES
from handwriting.render import render_notes
from handwriting.style import DEFAULT_STYLE_KEY, STYLES
from keyboards import style_keyboard

router = Router()

# user_id -> style key (in-memory; resets on restart, fine for MVP)
user_styles: dict[int, str] = {}

WELCOME = (
    "Assalomu alaykum! 📝\n\n"
    "Menga istalgan matnni yuboring — men uni xuddi qo'lda yozilgandek, "
    "ko'k siyohda, daftar varag'ida konspekt qilib chiqarib beraman.\n\n"
    "Maslahatlar:\n"
    "• Sarlavha uchun qatorni <code># </code> bilan boshlang\n"
    "• Ro'yxat band uchun qatorni <code>- </code> bilan boshlang\n"
    "• Bo'sh qator — yangi abzats\n\n"
    "Yozuv uslubini tanlash uchun /uslub buyrug'ini yuboring."
)


def _style_for(user_id: int):
    key = user_styles.get(user_id, DEFAULT_STYLE_KEY)
    return STYLES.get(key, STYLES[DEFAULT_STYLE_KEY])


@router.message(CommandStart())
async def on_start(message: Message):
    await message.answer(WELCOME, parse_mode="HTML", reply_markup=style_keyboard())


@router.message(Command("uslub"))
async def on_style_cmd(message: Message):
    await message.answer("Qaysi yozuv uslubida konspekt tayyorlay?", reply_markup=style_keyboard())


@router.callback_query(F.data.startswith("style:"))
async def on_style_chosen(callback: CallbackQuery):
    key = callback.data.split(":", 1)[1]
    if key not in STYLES:
        await callback.answer("Noma'lum uslub", show_alert=True)
        return
    user_styles[callback.from_user.id] = key
    await callback.answer(f"{STYLES[key].name} tanlandi ✅")
    await callback.message.edit_text(f"Uslub o'rnatildi: <b>{STYLES[key].name}</b>\n\nEndi menga matn yuboring.", parse_mode="HTML")


@router.message(F.text & ~F.text.startswith("/"))
async def on_text(message: Message):
    text = message.text.strip()
    if not text:
        return

    style = _style_for(message.from_user.id)
    await message.bot.send_chat_action(message.chat.id, "upload_photo")
    status = await message.answer("✍️ Yozilmoqda...")

    try:
        seed = random.randint(0, 1_000_000)
        pages = await asyncio.to_thread(render_notes, text, style, seed)
    except Exception:
        await status.edit_text("Kechirasiz, konspekt tayyorlashda xatolik yuz berdi. Qayta urinib ko'ring.")
        raise

    if len(pages) > MAX_PAGES:
        pages = pages[:MAX_PAGES]
        truncated = True
    else:
        truncated = False

    buffers = []
    for img in pages:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        buf.seek(0)
        buffers.append(buf)

    if len(buffers) == 1:
        await message.answer_photo(BufferedInputFile(buffers[0].read(), filename="konspekt.jpg"))
    else:
        for batch_start in range(0, len(buffers), 10):
            batch = buffers[batch_start:batch_start + 10]
            media = [
                InputMediaPhoto(media=BufferedInputFile(b.read(), filename=f"konspekt_{i}.jpg"))
                for i, b in enumerate(batch, start=batch_start)
            ]
            await message.answer_media_group(media)

    await status.delete()
    if truncated:
        await message.answer(f"⚠️ Matn juda uzun edi, faqat birinchi {MAX_PAGES} varaq tayyorlandi.")
