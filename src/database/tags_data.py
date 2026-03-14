import logging
from .connection import get_connection

logger = logging.getLogger(__name__)

async def init_tag_db():
    conn = None
    try:
        conn = await get_connection()
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id SERIAL PRIMARY KEY,
                tag TEXT
            );
        ''')
    except Exception as e:
        logger.error(f"Помилка ініціалізації бази тегів {e}")

    finally:
        if conn:
            await conn.close()

async def insert_tag(tag):
    try:
        conn = await get_connection()
        await conn.execute("INSERT INTO tags (tag) VALUES ($1)", tag)
        logger.info("Запис додано")

    except Exception as e:
        logger.error(f"Помилка при додаванні тега в базу {e}")

    finally:
        if conn:
            await conn.close()

async def del_tag(tag):
    try:
        conn = await get_connection()
        result = await conn.fetchrow("SELECT * FROM tags WHERE tag = $1", tag)

        if result:
            await conn.execute("DELETE FROM tags WHERE tag = $1", tag)
            logger.info("Тег видалено")
            return "success"
        
        else:
            logger.info("Тег не знайдено")
            return "no_tag"
        
    except Exception as e:
        logger.error(f"Помилка при видаленні тегу з бази {e}")

    finally:
        if conn:
            await conn.close()

async def update_tag(tag, value):
    try:
        conn = await get_connection()
        await conn.execute(f"UPDATE tags SET tag = $1 WHERE tag = $2", value, tag)
        logger.info("Тег в базі оновлено")

    except Exception as e:
        logger.error(f"Помилка при оновленні тега в базі {e}")

    finally:
        if conn:
            await conn.close()

async def get_tags():
    try:
        conn = await get_connection()
        rows = await conn.fetch("SELECT * FROM tags")

        if rows:
            return rows
        
        return[]
    
    except Exception as e:
        logger.error(f"Помилка діставання тегів as {e}")

    finally:
        if conn:
            await conn.close()