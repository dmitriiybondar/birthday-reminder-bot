import os
import sys
import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers.birthday_handlers.update_birthday import router as update_birthday_router
from handlers.birthday_handlers.list_birthday import router as list_birthdays_router
from handlers.birthday_handlers.del_birthday import router as delete_birthday_router
from handlers.birthday_handlers.add_birthday import router as add_birthday_router
from handlers.base_commands import router as base_router
from handlers.tag_handler import router as tag_router

from scheduler import send_reminders
from database.birthdays_data import init_birthday_db
from database.tags_data import init_tag_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    load_dotenv()
    await init_birthday_db()
    await init_tag_db()

    user = int(os.getenv("ADMIN_USER_ID"))
    bot = Bot(
        token=os.getenv("BOT_TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.include_router(tag_router)
    dp.include_router(base_router)
    dp.include_router(add_birthday_router)
    dp.include_router(list_birthdays_router)
    dp.include_router(delete_birthday_router)
    dp.include_router(update_birthday_router)

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
