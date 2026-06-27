from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Бот")

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Команда скасована")