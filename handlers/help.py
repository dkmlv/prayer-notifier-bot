from aiogram import types

from data import HELP_MESSAGE
from loader import dp


@dp.message_handler(commands="help", state="*")
@dp.throttled(rate=3)
async def give_help(message: types.Message):
    """Provide instructions on how to use the bot."""
    await message.answer(HELP_MESSAGE, disable_web_page_preview=True)
