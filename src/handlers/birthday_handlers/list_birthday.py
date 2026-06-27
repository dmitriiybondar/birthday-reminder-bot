import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command

from database.birthdays_data import select_by_tag, select_list
from handlers.tag_handler import get_tags
from states.birthday_states import ListBirthday

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("list"))
async def cmd_list(message: types.Message):
    try:
        names = await select_list()
        tags = await get_tags()

        if not names:
            await message.answer("Нема днів народження")
            return
        
        answer = "<b>Список днів народження:</b>\n\n"

        for tag in tags:
            full_list_by_tags = await select_by_tag(tag['tag'])

            if full_list_by_tags:
                answer += f"<b>{tag['tag']}:</b> \n"
                items = [f"{res['name']}: {res['date']}" for res in full_list_by_tags]
                answer += "\n".join(items) + "\n\n"

        await message.answer(answer)
        logger.info("Список надіслано")

    except Exception as e:
        await message.answer(f"Помилка {e}")
        logger.error(f"Поимлка {e}")


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

        await callback.message.delete()
        await callback.message.answer(answer)

    except Exception as e:
        await callback.message.answer("Помилка при виводі списку за тегом")
        logger.error(f"Помилка при виводі списку за тегом {e}")

    finally:
        await state.clear()
        await callback.answer()