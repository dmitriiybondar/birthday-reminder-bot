import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states.tag_states import Tag, EditTag
from database.tags_data import insert_tag, del_tag, update_tag, get_tags
from database.birthdays_data import update_name_with_tag

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("add_tag"))
async def cmd_add_tag(message: types.Message, state: FSMContext):
    await state.set_state(Tag.add_tag)
    await message.answer("Введіть новий тег")


@router.message(Command("delete_tag"))
async def cmd_delete_tag(message: types.Message, state: FSMContext):
    try:
        tags = await get_tags()
        builder = InlineKeyboardBuilder()

        for tag in tags:
            tag_name = tag["tag"]
            builder.add(
                types.InlineKeyboardButton(
                    text=tag_name,
                    callback_data=tag_name
                )
            )
        builder.adjust(3)
        keyboard = builder.as_markup()

        await state.set_state(Tag.delete_tag)
        await message.answer("Виберіть тег для видалення", reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Помилка видалення тегу {e}")
        await message.answer("Помилка видалення тегу")
        await state.clear()

@router.message(Command("edit_tag"))
async def cmd_edit_tag(message: types.Message, state: FSMContext):
    try:
        tags = await get_tags()
        builder = InlineKeyboardBuilder()

        for tag in tags:
            tag_name = tag["tag"]
            builder.add(
                types.InlineKeyboardButton(
                    text=tag_name,
                    callback_data=tag_name
                )
            )
        builder.adjust(3)
        keyboard = builder.as_markup()

        await state.set_state(EditTag.choose_tag)
        await message.answer("Виберіть тег для редагування", reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Помилка редагування тегу {e}")
        await message.answer("Помилка редагування тегу")
        await state.clear()

@router.message(Command("get_tags"))
async def cmd_get_tags(message: types.Message):
    try:
        tags = await get_tags()

        if tags:
            tag_list = [tag[1] for tag in tags]
            answer = "Список тегів:\n\n" + "\n".join(tag_list)
            await message.answer(answer)
        else:
            await message.answer("Тегів нема")

    except Exception as e:
        logger.error(f"Помилка при знаходженні тегів {e}")
        await message.answer("Помилка при знаходженні тегів")


@router.message(Tag.add_tag)
async def add_tag(message: types.Message, state: FSMContext):
    data = message.text

    try:
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
        await callback.message.delete_reply_markup()
        await callback.message.answer("Тег успішно видалено")
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

        await callback.message.delete_reply_markup()
        await callback.message.answer("Введіть нове значення")

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
        await message.answer("Тег оновлено")

    except Exception as e:
        logger.error(f"Помилка при редагуванні тегу {e}")
        await message.answer("Помилка при редагуванні тегу")
    
    finally:
        await state.clear()