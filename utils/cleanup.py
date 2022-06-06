from apscheduler.jobstores.base import JobLookupError

from loader import cities, sched, users
from utils.get_db_data import get_users_city


async def cleanup_user(tg_user_id: int):
    """Cleanup work to do after the user blocks the bot.

    This function will also be called if the user deletes their account.
    1. Get user's city.
    2. Delete user from users collection.
    3. Remove jobs scheduled for the user if they exist.
    4. Check if there are any users left who chose user's city.
        - If there are still users left, do nothing.
        - Else delete city from cities collection and remove job associated
          with the city.

    Parameters
    ----------
    tg_user_id : int
        Telegram user id
    """

    city = await get_users_city(tg_user_id)
    await users.delete_one({"tg_user_id": tg_user_id})

    scheduled_messages = [
        "Overview",
        "Fajr",
        "Dhuhr",
        "Asr",
        "Maghrib",
        "Isha",
    ]

    for scheduled_message in scheduled_messages:
        try:
            sched.remove_job(job_id=f"{scheduled_message}_{tg_user_id}")
        except JobLookupError:
            pass

    city_users = await users.find({"city": city}).to_list(None)

    if not city_users:
        await cities.delete_one({"city": city})
        try:
            sched.remove_job(job_id=f"Autoschedule_{city}")
        except JobLookupError:
            pass
