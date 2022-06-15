from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from data.constants import OPERATION_CANCELLED
from loader import dp


@dp.message_handler(commands="cancel", state="*")
async def cancel_current_operation(message: types.Message, state: FSMContext):
    """Reset state, inform operation was cancelled."""
    await state.finish()
    await message.answer(OPERATION_CANCELLED)
