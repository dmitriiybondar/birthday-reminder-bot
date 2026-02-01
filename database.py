import sqlite3
import logging

logger = logging.getLogger(__name__)


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


def select_list():
    try:
        conn = sqlite3.connect("birthday_db.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM birthdays")
        return cursor.fetchall()

    except Exception as e:
        logger.error(f"Помилка при надсиланні списку {e}")

    finally:
        conn.close()


def insert_birthday(name, date, tag):
    try:
        conn = sqlite3.connect("birthday_db.sqlite")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO birthdays (name, date, tag) VALUES (?, ?, ?)",
            (name, date, tag)
        )

        conn.commit()
        logger.info("Запис додано")

    except Exception as e:
        logger.error(f"Помилка при додаванні запису {e}")

    finally:
        conn.close()


def del_birthday(name):
    try:
        conn = sqlite3.connect("birthday_db.sqlite")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM birthdays WHERE name = ?", (name,))
        result = cursor.fetchone()
        
        if result:
            cursor.execute("DELETE FROM birthdays WHERE name = ?", (name,))
            conn.commit()

            logger.info(f"День народження {name} видалено")
            return "success"

        else:
            logger.info(f"Ім'я не знайдено {name}")
            return "no_name"

    except Exception as e:
        logger.error(f"помиилка при видаленні запису {e}")

    finally:
        conn.close()