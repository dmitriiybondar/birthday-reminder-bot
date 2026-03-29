import re
import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command

from database.birthdays_data import insert_birthday
from database.tags_data import get_tags

from states.birthday_states import AddBirthday
from keyboards import get_paginated_keyboard_tag

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("add_birthday"))
async def cmd_add_birthday(message: types.Message, state: FSMContext):
    await state.set_state(AddBirthday.add_name)
    await message.answer("Введіть ім'я")


@router.message(AddBirthday.add_name)
async def add_birthday_name(message: types.Message, state: FSMContext):
    try:
        await state.update_data(name=message.text)
        await message.answer("Введіть дату в форматі ДД.ММ")
        await state.set_state(AddBirthday.add_date)

    except Exception as e:
        await message.answer("Помилка додавання імені")
        logger.error(f"Помилка додавання імені {e}")
        await state.clear()


@router.message(AddBirthday.add_date)
async def add_birthday_date(message: types.Message, state: FSMContext):
    try:
        date = message.text
        tags = await get_tags()

        if not re.match(r"^\d{2}\.\d{2}", str(date).strip()):
            await message.answer("Введіть дату у формаі ДД.ММ")
            return
        await state.update_data(date=date)

        keyboard = get_paginated_keyboard_tag(tags, page=0)

        await message.answer("Виберіть тег:", reply_markup=keyboard)

    except Exception as e:
        await message.answer("Помилка додавання дати")
        logger.error(f"Помилка додавання дати {e}")
        await state.clear()


@router.callback_query(AddBirthday.add_date)
async def add_birthday_tag(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        tag = callback.data
        name = data["name"]
        date = data["date"]

        await insert_birthday(name, date, tag)
        await callback.message.delete()
        await callback.message.answer("Дані успішно додано")

    except Exception as e:
        await callback.message.answer("Помилка додавання даних")
        logger.error(f"Помилка додавання даних {e}")

    finally:
        await state.clear()
        await callback.answer()