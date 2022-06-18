import datetime as dt
import logging
from typing import Dict, Union

import aiohttp.client_exceptions as exceptions
from dateutil import tz

from data import GET_TIMES_URL
from loader import session


async def get_tz_info(city: str) -> Union[str, None]:
    """Get timezone information for a city.

    This is done by using the prayer calendar API.

    Parameters
    ----------
    city : str
        User's location, looks sth like: "Ari, Abruzzo, Italy"

    Returns
    -------
    str
        Timezone information string, like "Europe/Rome"
    """

    city_name, state_name, country_name = city.split(", ")

    params: Dict[str, Union[str, int]] = {
        "city": city_name,
        "country": country_name,
        "state": state_name,
    }

    try:
        async with session.get(GET_TIMES_URL, params=params) as resp:
            data = await resp.json(encoding="utf-8")
            try:
                resp.raise_for_status()
            except exceptions.ClientResponseError:
                logging.exception(f"GET request failed: {data.get('data')}")
            else:
                return data["data"][0]["meta"]["timezone"]
    except exceptions.ClientConnectorError as e:
        logging.exception(e)


def get_current_dt(tz_info: str) -> dt.datetime:
    """Get current date and time in the specified timezone.

    Parameters
    ----------
    tz_info : str
        Timezone information string, like "Europe/Rome"

    Returns
    -------
    dt.datetime
        Python datetime object
    """

    users_tz = tz.gettz(tz_info)
    current_dt = dt.datetime.now(users_tz)
    return current_dt


def get_tomorrows_dt(tz_info: str) -> dt.datetime:
    """Get tomorrow's date and time in the specified timezone.

    Parameters
    ----------
    tz_info : str
        Timezone information string, like "Europe/Rome"

    Returns
    -------
    dt.datetime
        Python datetime object
    """

    current_dt = get_current_dt(tz_info)
    tomorrows_dt = current_dt + dt.timedelta(days=1)
    return tomorrows_dt
