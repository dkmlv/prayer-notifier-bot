from typing import Tuple

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


async def get_users_city(tg_user_id: int) -> str:
    """Get user's city from the DB and return it.

    Parameters
    ----------
    tg_user_id : int
        User's Telegram id

    Returns
    -------
    str
        User's location, looks sth like: "Ari, Abruzzo, Italy"
    """

    user = await users.find_one({"tg_user_id": tg_user_id})
    return user["city"]
