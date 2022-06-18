"""This module is only responsible for returning today's hijri date."""

import datetime as dt

from hijri_converter import Gregorian

from loader import cities
from utils import get_tomorrows_dt


def get_hijri_date(gregorian_dt: dt.datetime) -> str:
    """Convert gregorian date and time to Hijri date.

    Parameters
    ----------
    gregorian_dt : dt.datetime
        Date and time in the Gregorian calendar

    Returns
    -------
    str
        Date and time in the Hijri calendar
    """

    year, month, day = gregorian_dt.year, gregorian_dt.month, gregorian_dt.day
    hijri = Gregorian(year, month, day).to_hijri()

    h_day = hijri.day
    h_month = hijri.month_name("en")
    h_year = hijri.year
    h_notation = hijri.notation("en")

    hijri_date = f"{h_day} {h_month} {h_year} {h_notation}"

    return hijri_date


async def update_hijri_date(city: str, tz_info: str) -> str:
    """Get tomorrow's hijri date and update it in the DB for a given city.

    Parameters
    ----------
    city : str
        User's location, looks sth like: "Ari, Abruzzo, Italy"
    tz_info : str
        Timezone information string, like "Europe/Rome"

    Returns
    -------
    str
        Tomorrow's date and time in the Hijri calendar
    """

    tomorrows_dt = get_tomorrows_dt(tz_info)
    hijri_date = get_hijri_date(tomorrows_dt)

    await cities.update_one(
        {"city": city}, {"$set": {"hijri_date": hijri_date}}, upsert=True
    )
    return hijri_date
