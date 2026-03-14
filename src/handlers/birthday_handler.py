import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.birthdays_data import select_list, insert_birthday, del_birthday, update_birthday, select_names, select_by_tag
from database.tags_data import get_tags
from states.birthday_states import AddBirthday, DeleteBirthday, EditBirthday

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


@router.message(Command("add_birthday"))
async def cmd_add_birthday(message: types.Message, state: FSMContext):
    await state.set_state(AddBirthday.add_name)
    await message.answer("Введіть ім'я")


@router.message(Command("delete_birthday"))
async def cmd_delete_birthday(message: types.Message, state: FSMContext):
    await state.set_state(DeleteBirthday.delete_birth)
    await message.answer("Введіть ім'я для видалення")


@router.message(Command("update_birthday"))
async def cmd_update_birthday(message: types.Message, state: FSMContext):
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

        await message.answer("Введіть ім'я для оновлення", reply_markup=keyboard)
        await state.set_state(EditBirthday.edit_name)

    except Exception as e:
        logger.error(f"Помилка вибору імені {e}")
        await message.answer("Помилка вибору імені")
        await state.clear()


@router.message(AddBirthday.add_name)
async def add_birthday_name(message: types.Message, state: FSMContext):
    try:
        await state.update_data(name=message.text)
        await message.answer("Введіть дату в форматі ДД.ММ")
        await state.set_state(AddBirthday.add_date)

    except Exception as e:
        await message.answer(f"Помилка додавання імені")
        logger.error("Помилка додавання імені")
        await state.clear()


@router.message(AddBirthday.add_date)
async def add_birthday_date(message: types.Message, state: FSMContext):
    try:
        await state.update_data(date=message.text)

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

        await message.answer("Виберіть тег:", reply_markup=keyboard)

    except Exception as e:
        await message.answer(f"Помилка додавання дати {e}")
        logger.error("Помилка додавання дати")
        await state.clear()


@router.callback_query(AddBirthday.add_date)
async def add_birthday_tag(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        tag = callback.data
        name = data["name"]
        date = data["date"]

        await insert_birthday(name, date, tag)
        await callback.message.answer("Дані успішно додавано")

    except Exception as e:
        await callback.message.answer("Помилка додавання даних")
        logger.error("Помилка додавання даних")

    finally:
        await state.clear()
        await callback.answer()

@router.message(DeleteBirthday.delete_birth)
async def delete_birthday(message: types.Message, state: FSMContext):
    name = message.text

    try:
        result = await del_birthday(name)
        if result == "success":
            await message.answer(f"День народження {name} видалено")
        else:
            await message.answer("Ім'я не знайдено")

    except Exception as e:
        await message.answer(f"Помилка при видаленні запису {e}")
        logging.error(f"Помилка при видаленні запису {e}")
    finally:
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
        await callback.message.answer("Запис оновлено")

    except Exception as e:
        await callback.message.answer("Помилка при оновлені запису")
        logger.error(f"Помилка при редагуванні даних {e}")

    finally:
        await state.clear()
        await callback.answer()