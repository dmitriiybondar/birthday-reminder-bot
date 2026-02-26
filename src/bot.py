import os
import sys
import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers.birthday_handler import router as birthday_router
from handlers.base_commands import router as base_router
from scheduler import send_reminders
from database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    load_dotenv()
    await init_db()

    user = int(os.getenv("ADMIN_USER_ID"))
    bot = Bot(
        token=os.getenv("BOT_TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.include_router(base_router)
    dp.include_router(birthday_router)

    scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")

    scheduler.add_job(
        send_reminders,
        trigger="cron",
        hour=12,
        minute=0,
        args=(bot, user, "today")
    )

    scheduler.add_job(
        send_reminders,
        trigger="cron",
        hour=22,
        minute=0,
        args=(bot, user, "tomorrow")
    )
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
