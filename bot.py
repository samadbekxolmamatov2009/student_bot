import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers import router


async def main():
    if not BOT_TOKEN:
        similar = [k for k in os.environ if "TOKEN" in k.upper() or "BOT" in k.upper()]
        hint = f" Shunga yaqin nomdagi o'zgaruvchilar topildi: {similar}." if similar else " Hech qanday mos o'zgaruvchi topilmadi — bu xizmatda umuman environment variable sozlanmagan."
        raise SystemExit(
            "BOT_TOKEN topilmadi. Render'da aynan shu xizmatning (Environment tab) "
            "Environment Variables bo'limiga 'BOT_TOKEN' nomi bilan qo'shing va qayta deploy qiling."
            + hint
        )

    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
