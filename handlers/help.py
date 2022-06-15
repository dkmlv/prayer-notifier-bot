from aiogram import types

from data.constants import HELP_MESSAGE
from loader import dp


@dp.message_handler(commands="help", state="*")
async def give_help(message: types.Message):
    """Provide some instructions on how to use the bot + brief info."""
    await message.answer(HELP_MESSAGE)
