import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command

from states.tag_states import Tag, EditTag
from states.birthday_states import ListBirthday
from database.tags_data import insert_tag, del_tag, update_tag, get_tags
from database.birthdays_data import update_name_with_tag
from keyboards import get_paginated_keyboard_tag


router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("list_tag"))
async def cmd_list_tag(message: types.Message, state: FSMContext):
    try:
        tags = await get_tags()
        if not tags:
            await message.answer("Немає тегів")
            return
    
        keyboard = get_paginated_keyboard_tag(tags, page=0)

        await message.answer("Виберіть тег", reply_markup=keyboard)
        await state.set_state(ListBirthday.choose_tag)

    except Exception as e:
        logger.error(f"Помилка вибору тегу {e}")
        await message.answer("Помилка вибору тегу")

@router.message(Command("add_tag"))
async def cmd_add_tag(message: types.Message, state: FSMContext):
    await state.set_state(Tag.add_tag)
    await message.answer("Введіть новий тег")


@router.message(Command("delete_tag"))
async def cmd_delete_tag(message: types.Message, state: FSMContext):
    try:
        tags = await get_tags()

        if not tags:
            await message.answer("Нема тегів")
            return

        keyboard = get_paginated_keyboard_tag(tags, page=0)
        await message.answer("Виберіть тег для видалення", reply_markup=keyboard)
        await state.set_state(Tag.delete_tag)

    except Exception as e:
        logger.error(f"Помилка видалення тегу {e}")
        await message.answer("Помилка видалення тегу")
        await state.clear()

@router.message(Command("edit_tag"))
async def cmd_edit_tag(message: types.Message, state: FSMContext):
    try:
        tags = await get_tags()

        if not tags:
            await message.answer("Нема тегів")
            return
        
        keyboard = get_paginated_keyboard_tag(tags, page=0)
        await message.answer("Виберіть тег для редагування", reply_markup=keyboard)
        await state.set_state(EditTag.choose_tag)

    except Exception as e:
        logger.error(f"Помилка редагування тегу {e}")
        await message.answer("Помилка редагування тегу")
        await state.clear()

@router.message(Command("get_tags"))
async def cmd_get_tags(message: types.Message):
    try:
        tags = await get_tags()

        if tags:
            tag_list = [tag["tag"] for tag in tags]
            answer = "Список тегів:\n\n" + "\n".join(tag_list)
            await message.answer(answer)
        else:
            await message.answer("Тегів нема")

    except Exception as e:
        logger.error(f"Помилка при знаходженні тегів {e}")
        await message.answer("Помилка при знаходженні тегів")


@router.message(Tag.add_tag)
async def add_tag(message: types.Message, state: FSMContext):
    try:
        data = message.text.strip()
        tags = await get_tags()
        if tags:
            tag_list = [tag["tag"] for tag in tags]

            if data in tag_list:
                await message.answer("Тег вже існує")
                return

        await insert_tag(data)
        await message.answer("Тег успішно додано")
    except Exception as e:
        logger.error(f"Помилка при додаванні тегу {e}")
        await message.answer("Помилка при додаванні тегу")
    finally:
        await state.clear()
        

@router.callback_query(Tag.delete_tag)
async def delete_tag(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = callback.data
        await del_tag(data)
        await callback.message.delete()
        await callback.message.answer(f"Тег '{data}' успішно видалено")
    except Exception as e:
        logger.error(f"Помилка при видаленні тегу {e}")
        await callback.message.answer("Помилка при видаленні тегу")
    finally:
        await state.clear()
        await callback.answer()


@router.callback_query(EditTag.choose_tag)
async def edit_tag_select(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.update_data(old_tag=callback.data)
        await state.set_state(EditTag.value)
        data = await state.get_data()

        await callback.message.delete()
        await callback.message.answer(f"Введіть нове значення для тегу '{data["old_tag"]}'")

    except Exception as e:
        logger.error(f"Помилка при знаходженні тегу {e}")
        await callback.message.answer("Помилка при знаходженні тегу")
        await state.clear()
        
    finally:
        await callback.answer()


@router.message(EditTag.value)
async def edit_tag_value(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        old_tag = data["old_tag"]
        new_tag = message.text

        await update_name_with_tag(new_tag, old_tag)
        await update_tag(old_tag, new_tag)
        await message.answer(f"Тег '{old_tag}' оновлено на '{new_tag}'")

    except Exception as e:
        logger.error(f"Помилка при редагуванні тегу {e}")
        await message.answer("Помилка при редагуванні тегу")
    
    finally:
        await state.clear()