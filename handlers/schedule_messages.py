"""
This part deals with the main functionality of the bot: scheduling reminders.
"""

import datetime as dt
import logging
from random import randint

import requests
from aiogram import types

from loader import bot, cities, sched, users


async def update_all():
    """
    Makes GET requests to the prayer times API and updates the prayer times.
    """
    city_data = cities.find({}, {"_id": 0})
    city_data = await city_data.to_list(length=100)

    for city in city_data:
        parameters = {"city": city["city"], "juristic": 1}
        response = requests.get(
            "https://api.pray.zone/v2/times/today.json", params=parameters
        )
        response.raise_for_status()

        response = response.json()
        times = response["results"]["datetime"][0]["times"]

        await cities.update_one({"city": city}, {"$set": {"times": times}})


async def send_reminder(some_id: int, txt: str):
    """
    Sends a reminder to the user.

    some_id -> user's id
    txt -> custom message to send to the user

    (source: https://docs.aiogram.dev/en/latest/telegram/index.html)
    """
    try:
        await bot.send_message(some_id, txt)
    except exceptions.BotBlocked:
        logging.error(f"Target [ID:{some_id}]: blocked by user")
        await users.delete_one({"user_id": some_id})
    except exceptions.ChatNotFound:
        logging.error(f"Target [ID:{some_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logging.error(
            f"Target [ID:{some_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds."
        )
        await asyncio.sleep(e.timeout)
        return await send_message(some_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        logging.error(f"Target [ID:{some_id}]: user is deactivated")
        await users.delete_one({"user_id": some_id})
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{some_id}]: failed")
    else:
        logging.info(f"Target [ID:{some_id}]: success")


async def schedule_one(message: types.Message):
    """
    Schedule reminders for one user (new user).
    This function will be called when a new user starts a chat with the bot.
    The 'message' argument refers to the city that the user will provide.
    """
    user_id = message.from_user.id
    city_name = message.text

    # find prayer times for this city (not ready to work with)
    times = await cities.find_one({"city": city_name})
    times = times["times"]

    # these times that we obtained from the API are not needed, so we pop them
    not_needed = ["Imsak", "Sunset", "Midnight"]
    for item in not_needed:
        times.pop(item)

    # sunrise time will be sent in the Fajr reminder
    sunrise = times.pop("Sunrise")

    now = dt.datetime.now()

    today = str(dt.date.today())

    # this dictionary will contain prayer times
    # (ready to work with, in datetime format)
    prayer_times = {}

    # loop through all the prayer times
    for item in times:
        # item here refers to prayer names (Fajr, Dhuhr, Asr, etc)
        time = times[item]

        # apscheduler requires a datetime object to be passed in, so we make it here
        prayer_time = dt.datetime.fromisoformat(today + " " + time)

        # if the time of the prayer is yet to come, include the prayer in
        # prayer_times
        # this is needed as the new user may set up with the bot at around
        # afternoon for example, and in this case the user won't need reminders
        # for Fajr
        if prayer_time > now:
            # there is a limit on how many messages can be sent in one second
            # by the bot, so we randomise the seconds
            seconds = dt.timedelta(seconds=randint(0, 59))
            # initially, prayer time does not have a seconds value
            prayer_time += seconds
            prayer_times[item] = prayer_time

    for item in prayer_times:
        # Fajr reminder is different since the sunrise time has to be mentioned
        if item == "Fajr":
            text = (
                "Time to pray for Fajr.\nMake sure that you pray before "
                "sunrise, which is at {}.".format(sunrise)
            )
        else:
            text = "Time to pray for {}.".format(item)

        # scheduling the reminder
        sched.add_job(
            send_reminder,
            "date",
            run_date=prayer_times[item],
            args=[user_id, text],
            id=str(user_id) + item,
            replace_existing=True,
        )


async def schedule_all():
    """
    Schedules reminders to pray for all users.
    This function is intended to be called once at the start of every day.
    """
    # update prayer times
    await update_all()

    city_data = cities.find({}, {"_id": 0})
    city_data = await city_data.to_list(length=100)

    for city in city_data:
        # city_times -> prayer times for that city
        city_times = city["times"]

        # these times that we obtained from the API are not needed, so we pop them
        not_needed = ["Imsak", "Sunset", "Midnight"]
        for item in not_needed:
            city_times.pop(item)

        # sunrise time will be sent in the Fajr reminder
        sunrise = city_times.pop("Sunrise")

        now = dt.datetime.now()
        today = str(dt.date.today())

        # this dictionary will contain prayer times
        # (ready to work with, in datetime format)
        prayer_times = {}

        for item in city_times:
            # item here refers to prayer names (Fajr, Dhuhr, Asr, etc)
            time = city_times[item]

            # apscheduler requires a datetime object to be passed in, so we make it here
            prayer_time = dt.datetime.fromisoformat(today + " " + time)

            prayer_times[item] = prayer_time

        # get all the users who live in this city
        city_users = users.find({"city": city["city"]})
        city_users = await city_users.to_list(length=10000)

        # number of seconds (can't send more than 30 messages per second, so yeah)
        secs = 0

        for index, user in enumerate(city_users):
            user_id = user["user_id"]

            # can't send more than 30 messages per sec, so every 20 messages,
            # we add a second
            if index % 20 == 0:
                secs += 1

            for item in prayer_times:
                # item here refers to prayer names (Fajr, Dhuhr, Asr, etc)
                time = prayer_times[item]
                seconds = dt.timedelta(seconds=secs)
                # initially, prayer time does not have a seconds value
                time += seconds

                # the Fajr reminder is different since the sunrise time has to
                # be mentioned
                if item == "Fajr":
                    text = (
                        "Time to pray for Fajr.\nMake sure that you pray before "
                        "sunrise, which is at {}.".format(sunrise)
                    )
                else:
                    text = "Time to pray for {}.".format(item)

                sched.add_job(
                    send_reminder,
                    "date",
                    run_date=time,
                    args=[user_id, text],
                    id=str(user_id) + item,
                    replace_existing=True,
                )


# scheduling reminders will occur every day at 2 am
# 2 am was picked since there are no prayers at this time
sched.add_job(schedule_all, "cron", day="*", hour=2)

