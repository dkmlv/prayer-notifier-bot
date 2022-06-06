import asyncio
import datetime as dt
import logging
import random
from typing import Dict

from aiogram import exceptions
from dateutil import parser

from data.constants import SUNRISE, TIME_TO_PRAY
from loader import bot, sched, users
from utils.cleanup import cleanup_user
from utils.hijri_date import update_hijri_date
from utils.prayer_times import generate_overview_msg, update_prayer_times


async def send_message(
    user_id: int, text: str, disable_notification: bool = False
) -> bool:
    """Safe messages sender

    Source: https://docs.aiogram.dev/en/latest/examples/broadcast_example.html

    Parameters
    ----------
    user_id : int
        Telegram user id
    text : str
        Text to send to the user
    disable_notification : bool
        Whether there should be a notification when the message is received, is
        set to False by default

    Returns
    -------
    bool
        True if message was sent, False otherwise
    """

    try:
        await bot.send_message(
            user_id, text, disable_notification=disable_notification
        )
    except exceptions.BotBlocked:
        logging.error(f"Target [ID:{user_id}]: blocked by user")
        await cleanup_user(user_id)
    except exceptions.ChatNotFound:
        logging.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds."
        )
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        logging.error(f"Target [ID:{user_id}]: user is deactivated")
        await cleanup_user(user_id)
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def schedule_one(
    tg_user_id: int,
    prayer_times: Dict[str, str],
    hijri_date: str,
    seconds: int = None,
):
    """Schedule reminders to pray for one user.

    Parameters
    ----------
    tg_user_id : int
        Telegram user id
    prayer_times : Dict[str, str]
        Prayer times for the user's city
    hijri_date : str
        Date in the Hijri calendar
    seconds : int
        The number of seconds to add to the prayer time. This is needed because
        Telegram has limits on how many messages can be sent per second.
    """

    if not seconds:
        seconds = random.randint(0, 59)

    sunrise = prayer_times.pop("Sunrise")

    for prayer, time in prayer_times.items():
        prayer_dt = parser.parse(time) + dt.timedelta(seconds=seconds)

        text = TIME_TO_PRAY.format(prayer)

        # Fajr reminder is different since the sunrise time has to be mentioned
        if prayer == "Fajr":
            text += "\n" + SUNRISE.format(sunrise)

        sched.add_job(
            send_message,
            "date",
            run_date=prayer_dt,
            args=[tg_user_id, text],
            id=f"{prayer}_{tg_user_id}",
            replace_existing=True,
            misfire_grace_time=600,
        )

    # this message will be sent out early morning before the fajr reminder
    overview_msg = await generate_overview_msg(
        tg_user_id, prayer_times, hijri_date
    )

    # u can pick any time u want, i just wanted to use this time
    fajr_time = prayer_times["Fajr"]
    fajr_dt = parser.parse(fajr_time)
    minutes = dt.timedelta(minutes=30, seconds=seconds)
    send_time = fajr_dt - minutes

    # scheduling the overview message containing prayer times for the day
    sched.add_job(
        send_message,
        "date",
        run_date=send_time,
        args=[tg_user_id, overview_msg],
        id=f"Overview_{tg_user_id}",
        misfire_grace_time=600,
    )


async def schedule_all(
    city: str, prayer_times: Dict[str, str], hijri_date: str
):
    """Schedule prayer reminders for all users in a given city.

    Parameters
    ----------
    location : str
        User's location, looks sth like: "Springfield, CO, US"
    prayer_times : Optional[dict]
        Prayer times for the given city
    hijri_date : str
        Hijri date, looks sth like: "3 Dhu al-Qi’dah 1443 AH"
    """

    city_users = await users.find({"city": city}).to_list(None)
    tg_user_ids = [user["tg_user_id"] for user in city_users]

    for index, tg_user_id in enumerate(tg_user_ids):
        seconds = index // 5  # 5 messages per second
        prayer_times_copy = prayer_times.copy()
        await schedule_one(tg_user_id, prayer_times_copy, hijri_date, seconds)


async def auto_schedule(city: str, tz_info: str):
    """Automatically schedule prayer reminders for tomorrow.

    1. Update prayer times for the city (get tomorrow's prayer times)
    2. Update the hijri date (get tomorrow's hijri date)
    3. Schedule reminders for everyone in that city
    4. Schedule self to run 15 minutes after tomorrow's last prayer

    Parameters
    ----------
    city : str
        User's location, looks sth like: "Ari, Abruzzo, Italy"
    tz_info : str
        Timezone information string, like "Europe/Rome"
    """

    prayer_times = await update_prayer_times(city, tz_info)

    try:
        assert prayer_times is not None
    except AssertionError:
        logging.error("Failed to update prayer times.")
    else:
        hijri_date = await update_hijri_date(city, tz_info)
        await schedule_all(city, prayer_times, hijri_date)

        last_prayer_dt = parser.parse(prayer_times["Isha"])

        run_dt = last_prayer_dt + dt.timedelta(minutes=15)
        sched.add_job(
            auto_schedule,
            "date",
            run_date=run_dt,
            args=[city, tz_info],
            id=f"Autoschedule_{city}",
            misfire_grace_time=3600,
        )
