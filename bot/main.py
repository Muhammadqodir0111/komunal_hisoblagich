import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .bot_config import BOT_TOKEN
from .handlers import router


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    print("=" * 40)
    print("BOT ISHGA TUSHDI")
    print("=" * 40)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())