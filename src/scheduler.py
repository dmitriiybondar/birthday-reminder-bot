from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import date, timedelta
from database import find_birthday
from aiogram import Bot

async def send_reminders(bot: Bot, user: int, day: str):
    if day == "tomorrow":
        birth_date = (date.today() + timedelta(days=1)).strftime("%d.%m")
        label = "Завтра"

    else:
        birth_date = date.today().strftime("%d.%m")
        label = "Сьогодні"

    rows = await find_birthday(birth_date)

    if rows:
        birthdays = [row["name"] for row in rows]
        answer = f"{label} день народження:\n\n" + "\n".join(birthdays)
        await  bot.send_message(user, answer)