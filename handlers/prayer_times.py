from aiogram import types

from loader import dp
from utils import generate_overview_msg


@dp.message_handler(commands="prayer_times")
async def prayer_times(message: types.Message):
    """Send today's prayer data."""
    tg_user_id = message.from_user.id
    overview_message = await generate_overview_msg(tg_user_id)
    await message.answer(overview_message)
