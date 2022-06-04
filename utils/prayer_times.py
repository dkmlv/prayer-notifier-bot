"""A simple GET request to the prayer times API."""

import datetime as dt
import logging
from typing import Dict, Optional, Union

import aiohttp.client_exceptions as exceptions
from dateutil import parser

from data.constants import GET_TIMES_URL, PRAYER_TIMES
from loader import cities, session
from utils.get_db_data import get_prayer_data, get_users_city
from utils.timezone import get_tomorrows_dt


async def get_prayer_times(
    city: str, dt_obj: dt.datetime
) -> Union[Dict[str, str], None]:
    """Return prayer times for the specified date for a certain city.

    This is done using the Aladhan Prayer Times Calendar API. For more info,
    check: https://aladhan.com/prayer-times-api#GetTimingsByCity

    Parameters
    ----------
    city : str
        New user's location, looks sth like: "Ari, Abruzzo, Italy"
    dt_obj : dt.datetime
        Python datetime object

    Returns
    -------
    Union[Dict[str, str], None]
        A dictionary with the prayer times if the request is successful, None
        otherwise
    """

    city_name, state_name, country_name = city.split(", ")
    day, month, year = dt_obj.day, dt_obj.month, dt_obj.year

    params: Dict[str, Union[str, int]] = {
        "city": city_name,
        "country": country_name,
        "state": state_name,
        "school": 1,
        "method": 3,
        "month": month,
        "year": year,
        "iso8601": "true",
    }

    try:
        async with session.get(GET_TIMES_URL, params=params) as resp:
            data = await resp.json(encoding="utf-8")
            try:
                resp.raise_for_status()
            except exceptions.ClientResponseError:
                logging.exception(f"GET request failed: {data.get('data')}")
            else:
                times = data["data"][day - 1]["timings"]
                times = process_prayer_times(times)
                return times
    except exceptions.ClientConnectorError as e:
        logging.exception(e)


def process_prayer_times(times: Dict[str, str]) -> Dict[str, str]:
    """It does what it says in the name.

    Remove redundant information from the prayer times.

    Parameters
    ----------
    times : Dict[str, str]
        Prayer times obtained directly from the API

    Returns
    -------
    Dict[str, str]
        Processed prayer times
    """

    not_needed = ["Imsak", "Sunset", "Midnight"]

    for item in not_needed:
        times.pop(item)

    # time will look like: "2022-06-01T04:03:00-06:00 (MDT)"
    times = {prayer: time.split()[0] for prayer, time in times.items()}

    return times


async def update_prayer_times(
    city: str, tz_info: str
) -> Union[Dict[str, str], None]:
    """Update prayer times for a given city.

    Makes a GET request to obtain prayer times for the next day. This function
    will be scheduled to run 15 minutes after the last prayer of the day.

    Parameters
    ----------
    city : str
        User's location, looks sth like: "Springfield, CO, US"
    tz_info : str
        Timezone information string, like "America/Denver"
    """

    tomorrows_dt = get_tomorrows_dt(tz_info)
    prayer_times = await get_prayer_times(city, tomorrows_dt)
    assert prayer_times is not None

    city_data = {"timings": prayer_times}
    await cities.update_one({"city": city}, {"$set": city_data}, upsert=True)
    return prayer_times


async def generate_overview_msg(
    tg_user_id: int,
    prayer_times: Optional[dict] = None,
    hijri_date: Optional[str] = None,
) -> str:
    """Generate an message containing the prayer times for the day.

    Looks like this:
        4 Dhu al-Qi’dah 1443 AH
        Here are your prayer times for today:

        Fajr:     02:47
        Dhuhr:    12:21
        Asr:      17:34
        Maghrib:  19:51
        Isha:     21:47

    Parameters
    ----------
    tg_user_id : int
        Telegram user id
    prayer_times : Optional[dict]
        Use these prayer times to generate the message, get them from DB if
        they are not passed in
    hijri_date : Optional[str]
        Use this hijri date to generate the message, if not passed in -> get
        it from DB

    Returns
    -------
    str
        An overview message containing the prayer times for the day
    """

    if not prayer_times and not hijri_date:
        city = await get_users_city(tg_user_id)
        prayer_times, hijri_date = await get_prayer_data(city)

    prayer_times.pop("Sunrise", None)  # type: ignore

    times = []
    for prayer, time in prayer_times.items():  # type: ignore
        prayer_dt = parser.parse(time)
        time = prayer_dt.strftime("%H:%M")
        times.append(f"<code>{prayer+':':10}{time}</code>")

    times = "\n".join(times)

    return PRAYER_TIMES.format(hijri_date, times)
