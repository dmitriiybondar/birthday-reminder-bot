import logging

from math import ceil
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.tags_data import get_tags
from database.birthdays_data import select_names

logger = logging.getLogger(__name__)

BUTTONS_PER_PAGE = 5

def get_paginated_keyboard(tags: list, page: int = 0):
    builder = InlineKeyboardBuilder()

    start_index = page * BUTTONS_PER_PAGE
    end_index = start_index + BUTTONS_PER_PAGE
    page_tags = tags[start_index:end_index]

    for tag in page_tags:
        tag_name = tag["tag"]
        builder.add(
            types.InlineKeyboardButton(
                text=tag_name,
                callback_data=tag_name
            )
        )

    builder.adjust(2)

    nav_buttons = []
    total_pages = ceil(len(tags) / BUTTONS_PER_PAGE)

    if page > 0:
        nav_buttons.append(
            types.InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"page_{page-1}"
            )
        )

    if page < total_pages - 1:
        nav_buttons.append(
            types.InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"page_{page+1}"
            )
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    return builder.as_markup()

async def tag_list():
    try:
        tags = await get_tags()
        builder = InlineKeyboardBuilder()

        for tag in tags:
            tag_name = tag["tag"]
            builder.add(
                types.InlineKeyboardButton(
                    text = tag_name,
                    callback_data=tag_name
                )
            )
        builder.adjust(3)
        keyboard = builder.as_markup()
        logger.info("Таги знайдено")

        return keyboard
    
    except Exception as e:
        logger.error(f"Теги не знайдено {e}")

async def people_list():
    try:
        people = await select_names()
        builder = InlineKeyboardBuilder()

        for name in people:
            builder.add(
                types.InlineKeyboardButton(
                    text=name,
                    callback_data=name
                )
            )
        builder.adjust(3)
        keyboard = builder.as_markup()
        logger.info("Імена знайдено")

        return keyboard
    
    except Exception as e:
        logger.error(f"Імена не знайдено {e}")