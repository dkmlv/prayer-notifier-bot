from aiogram import types

from loader import dp
from data.constants import HELP_MESSAGE


@dp.message_handler(commands="help", state="*")
async def give_help(message: types.Message):
    """Provide some instructions on how to use the bot + brief info."""
    await message.reply(HELP_MESSAGE)
