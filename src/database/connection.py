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