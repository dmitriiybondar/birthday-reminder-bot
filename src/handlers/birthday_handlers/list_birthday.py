import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command

from database.birthdays_data import select_by_tag
from database.tags_data import get_tags
from states.birthday_states import ListBirthday
from keybords import get_paginated_keyboard_tag

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("list"))
async def cmd_list(message: types.Message):
    try:
        tags = await get_tags()

        if not tags:
            await message.answer("Нема тегів")
            return
        
        answer = "<b>Список днів народження:</b>\n\n"

        for tag in tags:
            tag_name = tag["tag"]
            answer += f"<b>{tag_name}:</b> \n"

            full_list_by_tags = await select_by_tag(tag_name)

            if full_list_by_tags:
                items = [f"{res[1]}: {res[2]}" for res in full_list_by_tags]
                answer += "\n".join(items) + "\n\n"
            else:
                answer += "-Нема імен\n\n"

        await message.answer(answer)
        logger.info("Список надіслано")

    except Exception as e:
        await message.answer(f"Помилка {e}")
        logger.error(f"Поимлка {e}")


@router.message(Command("list_tag"))
async def cmd_list_tag(message: types.Message, state: FSMContext):
    try:
        tags = await get_tags()
        if not tags:
            await message.answer("Немає тегів")
    
        keyboard = get_paginated_keyboard_tag(tags, page=0)

        await message.answer("Виберіть тег", reply_markup=keyboard)
        await state.set_state(ListBirthday.choose_tag)

    except Exception as e:
        logger.error(f"Помилка вибору тегу {e}")
        await message.answer("Помилка вибору тегу")


@router.callback_query(ListBirthday.choose_tag)
async def list_tag(callback: types.CallbackQuery, state: FSMContext):
    try:
        value = callback.data
        answer = f"<b>Список днів народження за тегом '{value}':</b>\n\n"
        result = await select_by_tag(value)

        if result:
            items = [f"{res[1]}: {res[2]}" for res in result]
            answer += "\n".join(items) + "\n\n"
        else:
            answer += "Нема імен за цим тегом"

        await callback.message.delete_reply_markup()
        await callback.message.answer(answer)

    except Exception as e:
        await callback.message.answer("Помилка при виводі списку за тегом")
        logger.error(f"Помилка при виводі списку за тегом {e}")

    finally:
        await state.clear()
        await callback.answer()