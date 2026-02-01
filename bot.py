import asyncio
import os 
import sys
import logging
import sqlite3
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")

bot = Bot(
    token=bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


def init_db():
    conn = sqlite3.connect("birthday_db.sqlite")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS birthdays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            tag TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class Form(StatesGroup):
    add_birth = State()
    delete_birth = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Бот запущено")

@dp.message(Command("list"))
async def cmd_list(message: types.Message):
    try:
        conn = sqlite3.connect("birthday_db.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM birthdays")
        result = cursor.fetchall()

        if result:
            items = [f"{res[1]} - {res[2]}" for res in result]
            ans = "Список днів народження:\n\n" + "\n".join(items)

            await message.answer(ans)
            logger.info("Список надіслано")

        else:
            await message.answer("Нема записів")
            logger.warning("Нема записів")

    except Exception as e:
        await message.answer(f"Помилка {e}")
        logger.error(f"Помилка при надсиланні списку {e}")

    finally:
        conn.close()

@dp.message(Command("add_birthday"))
async def cmd_add_birthday(message: types.Message, state: FSMContext):
    await state.set_state(Form.add_birth)
    await message.answer("Введіть ім'я")

@dp.message(Command("delete_birthday"))
async def cmd_delete_birthday(message: types.Message, state: FSMContext):
    await state.set_state(Form.delete_birth)
    await message.answer("Введіть ім'я для видалення")

@dp.message(Form.add_birth)
async def add_birthday(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    if "name" not in data:
        await state.update_data(name=message.text)
        await message.answer("Введіть дату в форматі ДД.ММ")
        return
    
    if "date" not in data:
        await state.update_data(date=message.text)
        await message.answer("Введіть тег")
        return
    
    tag = message.text
    name = data["name"]
    date = data["date"]

    try:
        conn = sqlite3.connect("birthday_db.sqlite")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO birthdays (name, date, tag) VALUES (?, ?, ?)",
            (name, date, tag)
        )

        conn.commit()
        conn.close() 

        await message.answer("Запис додано")
        logger.info("Запис додано")
    
    except Exception as e:
        await message.answer("Помилка при додаванні запису")
        logger.error(f"Помилка при додаванні запису {e}")

    finally:
        await state.clear()

@dp.message(Form.delete_birth)
async def delete_birthday(message: types.Message, state: FSMContext):
    name = message.text

    try:
        conn = sqlite3.connect("birthday_db.sqlite")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM birthdays WHERE name = ?", (name,))
        result = cursor.fetchone()

        if result:
            cursor.execute("DELETE FROM birthdays WHERE name = ?", (name,))
            conn.commit()

            await message.answer(f"День народження {name} видалено")
            logger.info(f"День народження {name} видалено")

        else:
            await message.answer("Ім'я не знайдено")

    except Exception as e:
        await message.answer("Помилка при видаленні запису")
        logger.error(f"Помилка при видаленні запису {e}")

    finally:
        conn.close()
        await state.clear()


async def main():
    logger.info("Бот працює")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот вимкнено користувачем")
        print("Бот вимкнено користувачем")
    except Exception as e:
        logger.error(f"Виникла помилка: {e}")
        print(f"Виникла помилка: {e}")
        