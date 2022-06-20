from aiogram import types

from data import CAN_CANCEL, FIRST_TIME_USER, REGISTER_FIRST
from loader import dp, tracking, users
from states import Start
from utils import cleanup_user


@dp.message_handler(commands="settings")
async def show_settings(message: types.Message):
    """Show settings to the user."""
    tg_user_id = message.from_user.id
    user = await users.find_one({"tg_user_id": tg_user_id})

    if user:
        city = user["city"]
        tracking_on = await tracking.find_one({"tg_user_id": tg_user_id})

        tracking_status = "ON" if tracking_on else "OFF"

        keyboard = types.InlineKeyboardMarkup()
        buttons = [
            types.InlineKeyboardButton(
                "Reset All Settings",
                callback_data=f"ResetSettings_{tg_user_id}",
            ),
        ]
        keyboard.add(*buttons)
        text = (
            f"Here are your settings:\n<b>CITY:</b> {city}\n"
            f"<b>TRACKING:</b> {tracking_status}"
        )

        await message.answer(text, reply_markup=keyboard)
    else:
        await message.answer(REGISTER_FIRST)


@dp.callback_query_handler(text_startswith="ResetSettings_")
async def reset_all_settings(call: types.CallbackQuery):
    """Delete data associated with user and start registration again."""
    await call.answer()
    await call.message.delete_reply_markup()

    tg_user_id = int(call.data.split("_")[1])
    await cleanup_user(tg_user_id=tg_user_id)

    await call.message.edit_text(FIRST_TIME_USER)
    await call.message.answer(CAN_CANCEL)
    await Start.waiting_for_city.set()
