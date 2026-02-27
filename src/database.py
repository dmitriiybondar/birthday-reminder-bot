import asyncpg
import logging
import os

logger = logging.getLogger(__name__)

async def get_connection():
    try:
        return await asyncpg.connect(
            host=os.getenv("POSTGRES_HOST"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=5432
        )
    except Exception as e:
        logger.error(f"Помилка підключення {e}")
        return None

async def init_db():
    try:
        conn = await get_connection()
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS birthdays (
                id SERIAL PRIMARY KEY,
                name TEXT,
                date TEXT,
                tag TEXT
            )
        ''')

    except Exception as e:
        logger.error(f"Помилка ініціалізації бази {e}")

    finally:
        if conn:
            await conn.close()


async def select_list():
    try:
        conn = await get_connection()
        rows = await conn.fetch("SELECT * FROM birthdays")

        if rows:
            return rows
        
        return[]

    except Exception as e:
        logger.error(f"Помилка при надсиланні списку {e}")
        return[]

    finally:
        if conn:
            await conn.close()


async def select_names():
    try:
        conn = await get_connection()
        rows = await conn.fetch("SELECT name FROM birthdays")
        if rows:
            return [row[0] for row in rows]
        
        return[]
    
    except Exception as e:
        logger.error(f"Помилка при переборі імен {e}")
        return[]

    finally:
        if conn:
            await conn.close()

async def insert_birthday(name, date, tag):
    try:
        conn = await get_connection()
        await conn.execute(
            "INSERT INTO birthdays (name, date, tag) VALUES ($1, $2, $3)",
            name, date, tag
        )
        
        logger.info("Запис додано")

    except Exception as e:
        logger.error(f"Помилка при додаванні запису {e}")

    finally:
        if conn:
            await conn.close()


async def del_birthday(name):
    try:
        conn = await get_connection()

        result = await conn.fetchrow("SELECT * FROM birthdays WHERE name = $1", name)

        if result:
            await conn.execute("DELETE FROM birthdays WHERE name = $1", name)
            logger.info(f"День народження {name} видалено")
            return "success"

        else:
            logger.info(f"Ім'я не знайдено {name}")
            return "no_name"

    except Exception as e:
        logger.error(f"помиилка при видаленні запису {e}")

    finally:
        if conn:
            await conn.close()


async def update_birthday(name, column, value):
    try:
        conn = await get_connection()
        await conn.execute(f"UPDATE birthdays SET {column} = $1 WHERE name = $2", value, name)
        
        logger.info("Запис оновлено")

    except Exception as e:
        logger.error(f"Помилка при оновлені {e}")

    finally:
        if conn:
            await conn.close()

async def find_birthday(date):
    try:
        conn = await get_connection()
        rows = await conn.fetch("SELECT * FROM birthdays WHERE date = $1", date)
    
        if rows:
            logger.info("Дні народження знайдено в базі")
            return rows
        
        logger.info("Днів народження в базі не знайдено")
        return[]
    
    except Exception as e:
        logger.error("Помилка при перевірці дати")
        return[]

    finally:
        if conn:
            await conn.close()