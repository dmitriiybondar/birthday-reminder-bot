import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command

from database import select_list, insert_birthday, del_birthday, update_birthday, select_names
from states import Form, EditBirthday

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("list"))
async def cmd_list(message: types.Message):
    try:
        result = await select_list()

        if result:
            items = [f"{res[1]} - {res[2]}" for res in result]
            ans = "Список днів народження:\n\n" + "\n".join(items)

            await message.answer(ans)
            logger.info("Список надіслано")

        else:
            await message.answer("Нема записів")

    except Exception as e:
        await message.answer(f"Помилка {e}")
        logger.error(f"Поимлка {e}")


@router.message(Command("add_birthday"))
async def cmd_add_birthday(message: types.Message, state: FSMContext):
    await state.set_state(Form.add_birth)
    await message.answer("Введіть ім'я")


@router.message(Command("delete_birthday"))
async def cmd_delete_birthday(message: types.Message, state: FSMContext):
    await state.set_state(Form.delete_birth)
    await message.answer("Введіть ім'я для видалення")


@router.message(Command("update_birthday"))
async def cmd_update_birthday(message: types.Message, state: FSMContext):
    await state.set_state(EditBirthday.edit_name)
    await message.answer("Введіть ім'я для оновлення")


@router.message(Form.add_birth)
async def add_birthday(message: types.Message, state: FSMContext):
    data = await state.get_data()

    if "name" not in data:
        await state.update_data(name=message.text)
        await message.answer("Введіть дату в форматі ДД.ММ")
        return

    elif "date" not in data:
        await state.update_data(date=message.text)
        await message.answer("Введіть тег")
        return

    else:
        tag = message.text
        name = data["name"]
        date = data["date"]

        try:
            await insert_birthday(name, date, tag)
            await message.answer("Запис додано")
        except:
            await message.answer("Помилка додавання запису")
        finally:
            await state.clear()


@router.message(Form.delete_birth)
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


@router.message(EditBirthday.edit_name)
async def edit_birthday_name(message: types.Message, state: FSMContext):
    all_names = await select_names()

    if message.text.lower().strip() not in [name.lower() for name in all_names]:
        await message.answer("Нема такої людини")
        return
    
    await state.update_data(edit_name=message.text)

    buttons = [
        [
            types.InlineKeyboardButton(text="Ім'я", callback_data="name"),
            types.InlineKeyboardButton(text="Дата", callback_data="date"),
            types.InlineKeyboardButton(text="Тег", callback_data="tag")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer("Виберіть параметр для зміни", reply_markup=keyboard)
    await state.set_state(EditBirthday.select_field)

@router.callback_query(EditBirthday.select_field)
async def edit_birthday_date(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data
    await state.update_data(edit_column=choice)
    await callback.message.answer("Введіть нове значення")
    await state.set_state(EditBirthday.value)
    await callback.answer()


@router.message(EditBirthday.value)
async def edit_birthday_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    value = message.text
    name = data["edit_name"]
    column = data["edit_column"]

    try:
        await update_birthday(name, column, value)
        await message.answer("Запис оновлено")
    except:
        await message.answer("Помилка при оновлені запису")
    finally:
        await state.clear()

