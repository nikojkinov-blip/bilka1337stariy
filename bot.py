import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден!")

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

from handlers.start import router as start_router
from handlers.numbers import router as numbers_router

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(start_router)
dp.include_router(numbers_router)

async def main():
    print("📱 BeelineNumbers запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())