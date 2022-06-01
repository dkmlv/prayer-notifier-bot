from loader import users
from utils.city import process_city
from utils.schedule import schedule_one


async def register_user(tg_user_id: int, location: str):
    """Set up a new user to receieve prayer reminders.

    1. Add user to users collection
    2. Process user's city
    3. Schedule reminders for the user

    Parameters
    ----------
    tg_user_id : int
        Telegram user id of the new user
    location : str
        New user's location, looks sth like: "Springfield, CO, US"
    """

    await users.insert_one({"tg_user_id": tg_user_id, "location": location})
    await process_city(location)
    await schedule_one(tg_user_id, location)
