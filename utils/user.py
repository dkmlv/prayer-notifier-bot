from data import SETUP_DONE, SOMETHING_WRONG
from loader import dp, tracking, users
from utils import (
    get_prayer_data,
    process_city,
    schedule_calendar_gen,
    schedule_one,
)


async def register_user(tg_user_id: int, city: str):
    """Set up a new user to receieve prayer reminders.

    1. Process user's city
    2. Add user to users collection
    3. Schedule reminders for the user

    Parameters
    ----------
    tg_user_id : int
        Telegram user id of the new user
    city : str
        New user's location, looks sth like: "Ari, Abruzzo, Italy"
    """

    processed = await process_city(city)

    if not processed:
        await tracking.delete_one({"tg_user_id": tg_user_id})
        await dp.bot.send_message(tg_user_id, SOMETHING_WRONG)
    else:
        await users.insert_one({"tg_user_id": tg_user_id, "city": city})
        prayer_times, hijri_date = await get_prayer_data(city)
        await schedule_one(tg_user_id, prayer_times, hijri_date)

        tracking_on = await tracking.find_one({"tg_user_id": tg_user_id})
        if tracking_on:
            await schedule_calendar_gen(tg_user_id)

        await dp.bot.send_message(tg_user_id, SETUP_DONE)
