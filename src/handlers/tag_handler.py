import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command

from states.tag_states import Tag, EditTag
from database.tags_data import insert_tag, del_tag, update_tag, get_tags

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("add_tag"))
async def cmd_add_tag(message: types.Message, state: FSMContext):
    await state.set_state(Tag.add_tag)
    await message.answer("Введіть новий тег")

@router.message(Command("delete_tag"))
async def cmd_add_tag(message: types.Message, state: FSMContext):
    await state.set_state(Tag.delete_tag)
    await message.answer("Виберіть тег для видалення")

@router.message(Command("edit_tag"))
async def cmd_add_tag(message: types.Message, state: FSMContext):
    await state.set_state(EditTag.choose_tag)
    await message.answer("Виберіть тег для редагування")

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
        
@router.message(Tag.delete_tag)
async def delete_tag(message: types.Message, state: FSMContext):
    data = message.text

    try:
        await del_tag(data)
        await message.answer("Тег успішно видалено")
    except Exception as e:
        logger.error(f"Помилка при видаленні тегу {e}")
        await message.answer("Помилка при видаленні тегу")
    finally:
        state.clear()

@router.message(EditTag.choose_tag)
async def edit_tag_select(message: types.Message, state: FSMContext):
    try:
        data = message.text
        tags = await get_tags()
        
        if data.lower().strip() not in [tag["tag"].lower() for tag in tags]:
            await message.answer("Такого тегу не знайдено")
            return
    
        await state.update_data(tag=data)
        await state.set_state(EditTag.value)

        await message.answer("Введіть нове значення")
    except Exception as e:
        logger.error(f"Помилка при знаходженні тегу {e}")
        await message.answer("Помилка при знаходженні тегу")


@router.message(EditTag.value)
async def edit_tag_value(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        old_tag = data["tag"]
        new_tag = message.text

        await update_tag(old_tag, new_tag)
        await message.answer("Тег оновлено")

    except Exception as e:
        logger.error(f"Помилка при редагуванні тегу {e}")
        await message.answer("Помилка при редагуванні тегу")
    
    finally:
        await state.clear()