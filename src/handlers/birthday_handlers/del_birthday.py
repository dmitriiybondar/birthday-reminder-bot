import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command

from database.birthdays_data import del_birthday, select_names
from states.birthday_states import DeleteBirthday
from keyboards import get_paginated_keyboard_names

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("delete_birthday"))
async def cmd_delete_birthday(message: types.Message, state: FSMContext):
    try:
        names = await select_names()

        if not names:
            await message.answer("Немає імен")

        keyboard = get_paginated_keyboard_names(names, page=0)

        await message.answer("Введіть ім'я для видалення", reply_markup=keyboard)
        await state.set_state(DeleteBirthday.delete_birth)

    except Exception as e:
        logger.error(f"Помилка вибору імені {e}", exc_info=True)
        await message.answer("Помилка вибору імені")
        await state.clear()


@router.callback_query(DeleteBirthday.delete_birth)
async def delete_birthday(callback: types.CallbackQuery, state: FSMContext):
    try:
        name = callback.data
        result = await del_birthday(name)
        await callback.message.delete_reply_markup()

        if result == "success":
            await callback.message.answer(f"День народження {name} видалено")
        else:
            await callback.message.answer("Ім'я не знайдено")

    except Exception as e:
        await callback.message.answer(f"Помилка при видаленні запису {e}")
        logging.error(f"Помилка при видаленні запису {e}")
    finally:
        await state.clear()