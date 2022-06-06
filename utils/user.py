from data.constants import SETUP_DONE, SOMETHING_WRONG
from loader import dp, users
from utils.city import process_city
from utils.get_db_data import get_prayer_data
from utils.schedule import schedule_one


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
        await dp.bot.send_message(tg_user_id, SOMETHING_WRONG)
    else:
        await users.insert_one({"tg_user_id": tg_user_id, "city": city})
        prayer_times, hijri_date = await get_prayer_data(city)
        await schedule_one(tg_user_id, prayer_times, hijri_date)
        await dp.bot.send_message(tg_user_id, SETUP_DONE)
