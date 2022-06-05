from loader import users
from utils.city import process_city
from utils.get_db_data import get_prayer_data
from utils.schedule import schedule_one


async def register_user(tg_user_id: int, city: str):
    """Set up a new user to receieve prayer reminders.

    1. Add user to users collection
    2. Process user's city
    3. Schedule reminders for the user

    Parameters
    ----------
    tg_user_id : int
        Telegram user id of the new user
    city : str
        New user's location, looks sth like: "Ari, Abruzzo, Italy"
    """

    await users.insert_one({"tg_user_id": tg_user_id, "city": city})
    await process_city(city)

    prayer_times, hijri_date = await get_prayer_data(city)
    await schedule_one(tg_user_id, prayer_times, hijri_date)
