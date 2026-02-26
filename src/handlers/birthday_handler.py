import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from database import select_list, insert_birthday, del_birthday, update_birthday, select_names
from states import Form

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("list"))
async def cmd_list(message: Message):
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
async def cmd_add_birthday(message: Message, state: FSMContext):
    await state.set_state(Form.add_birth)
    await message.answer("Введіть ім'я")


@router.message(Command("delete_birthday"))
async def cmd_delete_birthday(message: Message, state: FSMContext):
    await state.set_state(Form.delete_birth)
    await message.answer("Введіть ім'я для видалення")


@router.message(Command("update_birthday"))
async def cmd_update_birthday(message: Message, state: FSMContext):
    await state.set_state(Form.edit_birth)
    await message.answer("Введіть ім'я для оновлення")


@router.message(Form.add_birth)
async def add_birthday(message: Message, state: FSMContext):
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
async def delete_birthday(message: Message, state: FSMContext):
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


@router.message(Form.edit_birth)
async def edit_birthday(message: Message, state: FSMContext):
    data = await state.get_data()
    columns = ["name", "date", "tag"]

    if "target_name" not in data:
        all_names = await select_names()

        if message.text.lower().strip() not in [name.lower() for name in all_names]:
            await message.answer("Нема такої людини")
            return
        
        await state.update_data(target_name=message.text)
        await message.answer("Виберіть параметр для зміни (name, date, tag)")
        return

    elif "column" not in data:
        choice = message.text.lower().strip()

        if choice not in columns:
            await message.answer("Параметр має бути один з (name, date, tag)")
            return

        await state.update_data(column=choice)
        await message.answer("Ввежіть нове значення")
        return

    else:
        value = message.text
        target = data["target_name"]
        column = data["column"]

        try:
            await update_birthday(target, column, value)
            await message.answer("Запис оновлено")
        except:
            await message.answer("Помилка при оновлені запису")
        finally:
            await state.clear()
