import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from database import select_list, insert_birthday, del_birthday
from states import Form

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("list"))
async def cmd_list(message: Message):
    try:
        result = select_list()

        if result:
            items = [f"{res[1]} - {res[2]}" for res in result]
            ans = "Список днів народження:\n\n" + "\n".join(items)

            await message.answer(ans)
            logger.info("Список надіслано")

        else:
            await message.answer("Нема записів")
            logger.warning("Нема записів")

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


@router.message(Form.add_birth)
async def add_birthday(message: Message, state: FSMContext):
    data = await state.get_data()

    if "name" not in data:
        await state.update_data(name=message.text)
        await message.answer("Введіть дату в форматі ДД.ММ")
        return

    if "date" not in data:
        await state.update_data(date=message.text)
        await message.answer("Введіть тег")
        return

    tag = message.text
    name = data["name"]
    date = data["date"]

    try:
        insert_birthday(name, date, tag)
        await message.answer("Запис додано")

    except:
        await message.answer("Помилка додавання запису")

    finally:
        await state.clear()


@router.message(Form.delete_birth)
async def delete_birthday(message: Message, state: FSMContext):
    name = message.text

    try:
        result = del_birthday(name)

        if result == "success":
            await message.answer(f"День народження {name} видалено")
        
        else:
            await message.answer("Ім'я не знайдено")

        
    except Exception as e:
        await message.answer(f"Помилка при видаленні запису {e}")
        logging.error(f"Помилка при видаленні запису {e}")

    finally:
        await state.clear()
