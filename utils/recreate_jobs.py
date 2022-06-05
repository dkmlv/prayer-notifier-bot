from loader import cities
from utils.city import setup_city
from utils.get_db_data import get_prayer_data
from utils.schedule import schedule_all


async def recreate_jobs():
    """Recreate jobs for the apscheduler.

    This function will be called on startup. Updates prayer times and schedules
    reminders for everyone.
    """

    user_cities = await cities.find().to_list(None)
    user_cities = [city["city"] for city in user_cities]

    for city in user_cities:
        await setup_city(city)
        prayer_times, hijri_date = await get_prayer_data(city)
        await schedule_all(city, prayer_times, hijri_date)
