from aiogram import types

from data import PLEASE_WAIT
from loader import dp, tracking


@dp.callback_query_handler(text_startswith=["Prayed_", "Late_", "NotPrayed"])
async def mark_prayer(call: types.CallbackQuery):
    """Mark the prayer in tracking collection."""
    await call.answer()
    await call.message.delete_reply_markup()

    if call.data != "NotPrayed":
        await call.message.edit_text(PLEASE_WAIT)

        status, prayer, month_name, day, year = call.data.split("_")
        await tracking.update_one(
            {"tg_user_id": call.from_user.id},
            {
                "$set": {
                    f"{year}.{month_name}.days.{int(day) - 1}.{prayer}": status
                }
            },
        )

    await call.message.edit_text("Noted, thank you!")
