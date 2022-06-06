import datetime as dt

from dateutil import parser

from loader import cities, sched
from utils.hijri_date import get_hijri_date
from utils.prayer_times import get_prayer_times
from utils.schedule import auto_schedule
from utils.timezone import get_current_dt, get_tz_info


async def setup_city(city: str) -> bool:
    """Get prayer times for the city and set up automatic scheduling.

    1. Get timezone information for the city.
    2. Get prayer times for today (the day is determined using timezone info)
        - If any prayers are left for today, insert today's prayer times to DB.
        - Else get tomorrow's prayer times and insert them to DB.
    3. Set up automatic scheduling.

    Parameters
    ----------
    city : str
        User's location, looks sth like: "Ari, Abruzzo, Italy"

    Returns
    -------
    bool
        True if setup was successful, False otherwise
    """

    tz_info = await get_tz_info(city)
    if not tz_info:
        return False

    gregorian_dt = current_dt = get_current_dt(tz_info)
    prayer_times = await get_prayer_times(city, current_dt)
    if not prayer_times:
        return False

    last_prayer_dt = parser.parse(prayer_times["Isha"])

    if current_dt > last_prayer_dt:
        # no prayers left for today
        gregorian_dt = tomorrow_dt = current_dt + dt.timedelta(days=1)
        prayer_times = await get_prayer_times(city, tomorrow_dt)
        if not prayer_times:
            return False
        last_prayer_dt = parser.parse(prayer_times["Isha"])

    hijri_date = get_hijri_date(gregorian_dt)
    city_data = {
        "city": city,
        "timezone": tz_info,
        "hijri_date": hijri_date,
        "timings": prayer_times,
    }
    await cities.update_one({"city": city}, {"$set": city_data}, upsert=True)

    run_dt = last_prayer_dt + dt.timedelta(minutes=15)
    sched.add_job(
        auto_schedule,
        "date",
        run_date=run_dt,
        args=[city, tz_info],
        id="Autoschedule_" + city,
        misfire_grace_time=3600,
    )

    return True


async def process_city(city: str) -> bool:
    """Process city information.

    Check whether city exists in DB and set it up if it doesn't.

    Parameters
    ----------
    city : str
        User's location, looks sth like: "Ari, Abruzzo, Italy"

    Returns
    -------
    bool
        True if city is set up successfully or city already exists in DB, False
        otherwise
    """

    document = await cities.find_one({"city": city})

    if not document:
        setup_successful = await setup_city(city)
        return setup_successful

    return True
