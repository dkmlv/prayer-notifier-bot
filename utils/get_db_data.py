from typing import Tuple, Union

from loader import cities, users


async def get_prayer_data(city: str) -> Tuple[dict, str]:
    """Return prayer data obtained from the DB.

    Parameters
    ----------
    city : str
        User's location, looks sth like: "Ari, Abruzzo, Italy"

    Returns
    -------
    Tuple[dict, str]
        Prayer times and hijri date
    """

    city_data = await cities.find_one({"city": city})
    prayer_times, hijri_date = (
        city_data["timings"],
        city_data["hijri_date"],
    )
    return prayer_times, hijri_date


async def get_users_city(tg_user_id: int) -> Union[str, None]:
    """Get user's city from the DB and return it.

    Parameters
    ----------
    tg_user_id : int
        User's Telegram id

    Returns
    -------
    str
        User's location, looks sth like: "Ari, Abruzzo, Italy". If the user
        does not exist in DB yet, return None.
    """

    user = await users.find_one({"tg_user_id": tg_user_id})

    if user:
        return user.get("city")


async def get_users_timezone(tg_user_id: int) -> Union[str, None]:
    """Get user's timezone from the DB and return it.

    Parameters
    ----------
    tg_user_id : int
        User's Telegram id

    Returns
    -------
    str
        Timezone information string, like "Europe/Rome"
    """

    users_city = await get_users_city(tg_user_id)

    if users_city:
        city = await cities.find_one({"city": users_city})
        return city.get("timezone")
