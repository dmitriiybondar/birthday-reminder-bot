import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command

from database.birthdays_data import update_birthday, select_names
from database.tags_data import get_tags

from states.birthday_states import EditBirthday
from keybords import get_paginated_keyboard_tag, get_paginated_keyboard_names

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("update_birthday"))
async def cmd_update_birthday(message: types.Message, state: FSMContext):
    try:
        people = await select_names()
        keyboard = get_paginated_keyboard_names(people, page=0)

        await message.answer("Введіть ім'я для оновлення", reply_markup=keyboard)
        await state.set_state(EditBirthday.edit_name)

    except Exception as e:
        logger.error(f"Помилка вибору імені {e}")
        await message.answer("Помилка вибору імені")
        await state.clear()


@router.callback_query(EditBirthday.edit_name)
async def edit_birthday_name(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = callback.data
        await state.update_data(edit_name=data)

        buttons = [
            [
                types.InlineKeyboardButton(text="Ім'я", callback_data="name"),
                types.InlineKeyboardButton(text="Дата", callback_data="date"),
                types.InlineKeyboardButton(text="Тег", callback_data="tag")
            ]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback.message.delete_reply_markup()
        await callback.message.answer("Виберіть параметр для зміни", reply_markup=keyboard)
        await state.set_state(EditBirthday.select_field)

    except Exception as e:
        logger.error(f"Помилка при редагуванні імені {e}")
        await callback.message.answer("Помилка при редагуванні імені")
        await state.clear()

@router.callback_query(EditBirthday.select_field)
async def edit_birthday_date(callback: types.CallbackQuery, state: FSMContext):
    try:
        choice = callback.data
        await state.update_data(edit_column=choice)

        if choice != "tag":
            await callback.message.answer("Введіть нове значення")
            await state.set_state(EditBirthday.value)

        else:
            tags = await get_tags()
            keyboard = get_paginated_keyboard_tag(tags, page=0)

            await callback.message.delete_reply_markup()
            await callback.message.answer("Виберіть новий тег", reply_markup=keyboard)
            await state.set_state(EditBirthday.tag_value)

    except Exception as e:
        logger.error(f"Помилка при виборі поля для редагуавання {e}")
        await callback.message.answer("Помилка при виборі поля для редагуавання")

    finally:
        await callback.answer()


@router.message(EditBirthday.value)
async def edit_birthday_value(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        
        value = message.text
        name = data["edit_name"]
        column = data["edit_column"]

        await update_birthday(name, column, value)
        await message.answer("Запис оновлено")

    except Exception as e:
        await message.answer("Помилка при оновлені запису")
        logger.error(f"Помилка при редагуванні даних {e}")
    finally:
        await state.clear()


@router.callback_query(EditBirthday.tag_value)
async def edit_birthday_tag(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()

        value = callback.data
        name = data["edit_name"]
        column = data["edit_column"]

        await update_birthday(name, column, value)
        await callback.message.delete_reply_markup()
        await callback.message.answer("Запис оновлено")

    except Exception as e:
        await callback.message.answer("Помилка при оновлені запису")
        logger.error(f"Помилка при редагуванні даних {e}")

    finally:
        await state.clear()
        await callback.answer()