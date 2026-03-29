import logging

from aiogram import Router, types, F
from database.birthdays_data import select_names
from database.tags_data import get_tags
from keybords import get_paginated_keyboard_names, get_paginated_keyboard_tag

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data.startswith("pageName_"))
async def paginated_names(callback: types.CallbackQuery):
    try:
        page = int(callback.data.split("_")[1])
        names = await select_names()
        keyboard = get_paginated_keyboard_names(names, page=page)

        await callback.message.edit_reply_markup(reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Помилка пагінації {e}", exc_info=True)
        await callback.message.answer("Помилка завантаження сторінки")
    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("pageTag_"))
async def paginated_tags(callback: types.CallbackQuery):
    try:
        page = int(callback.data.split("_")[1])
        tags = await get_tags()

        keyboard = get_paginated_keyboard_tag(tags, page=page)

        await callback.message.edit_reply_markup(reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Помилка пагінації {e}", exc_info=True)
        await callback.message.answer("Помилка завантаження сторінки")
    finally:
        await callback.answer()