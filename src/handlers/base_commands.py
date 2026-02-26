from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Бот запущено")