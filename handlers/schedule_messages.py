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
    Also updates today's date in Hijri calendar.
    """
    city_data = cities.find({}, {"_id": 0})
    city_data = await city_data.to_list(length=100)

    today = dt.date.today()

    day = today.day
    month = today.month
    year = today.year

    for city in city_data:
        parameters = {
            "city": city["city"],
            "country": "Uzbekistan",
            "school": 1,
            "method": 3,
            "month": month,
            "year": year,
        }
        response = requests.get(
            "http://api.aladhan.com/v1/calendarByCity", params=parameters
        )
        response.raise_for_status()

        response = response.json()

        today_data = response["data"][day - 1]
        times = today_data["timings"]

        hijri_data = today_data["date"]["hijri"]
        h_day = hijri_data["day"]
        h_month = hijri_data["month"]["en"]
        h_year = hijri_data["year"]
        h_designation = hijri_data["designation"]["abbreviated"]

        hijri_date = f"<b>{h_day} {h_month} {h_year} {h_designation}</b>\n"

        await cities.update_one(
            {"city": city["city"]},
            {"$set": {"times": times, "hijri_date": hijri_date}},
        )


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
        return await send_message(some_id, txt)  # Recursive call
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

    prayer_data = await cities.find_one({"city": city_name})
    prayer_times = prayer_data["times"]
    hijri_date = prayer_data["hijri_date"]

    # these times that we obtained from the API are not needed, so we pop them
    not_needed = ["Imsak", "Sunset", "Midnight"]
    for item in not_needed:
        prayer_times.pop(item)

    # sunrise time will be sent in the Fajr reminder
    sunrise = prayer_times.pop("Sunrise")

    today = str(dt.date.today())

    # this message will be sent out early morning before the fajr reminder
    overview_msg = hijri_date + "\nHere are your prayer times for today:"

    for prayer, time in prayer_times.items():
        overview_msg += f"\n<code>{prayer+':':10}{time}</code>"

        # apscheduler requires a datetime object to be passed in, so we make it here
        # slicing is done because time is provided like: "04:54 (+05)"
        prayer_time = dt.datetime.fromisoformat(today + " " + time[:5])

        # there is a limit on how many messages can be sent in one second
        # by the bot, so we randomise the seconds
        seconds = dt.timedelta(seconds=randint(0, 59))
        # initially, prayer time does not have a seconds value
        prayer_time += seconds

        # Fajr reminder is different since the sunrise time has to be mentioned
        if prayer == "Fajr":
            text = (
                "Time to pray Fajr.\nMake sure that you pray before "
                "sunrise, which is at {}.".format(sunrise)
            )
        else:
            text = "Time to pray {}.".format(prayer)

        # scheduling the reminder
        sched.add_job(
            send_reminder,
            "date",
            run_date=prayer_time,
            args=[user_id, text],
            id=str(user_id) + "_" + prayer,
            replace_existing=True,
        )

    # u can pick any time u want, i just wanted to use this time
    fajr_time = prayer_times["Fajr"]
    fajr_time = dt.datetime.fromisoformat(today + " " + fajr_time[:5])
    minutes = dt.timedelta(minutes=30, seconds=index)
    send_time = fajr_time - minutes

    sched.add_job(
        send_reminder,
        "date",
        run_date=send_time,
        args=[user_id, overview_msg],
        id=str(user_id) + "_overview",
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
        prayer_times = city["times"]
        hijri_date = city["hijri_date"]

        # these times that we obtained from the API are not needed, so we pop them
        not_needed = ["Imsak", "Sunset", "Midnight"]
        for item in not_needed:
            prayer_times.pop(item)

        # sunrise time will be sent in the Fajr reminder
        sunrise = prayer_times.pop("Sunrise")

        today = str(dt.date.today())

        # get all the users who live in this city
        city_users = users.find({"city": city["city"]})
        city_users = await city_users.to_list(length=10000)

        # number of seconds (can't send more than 30 messages per second, so yeah)
        secs = 0

        # this message will be sent out early morning before the fajr reminder
        overview_msg = hijri_date + "\nHere are your prayer times for today:"

        for index, user in enumerate(city_users):
            user_id = user["user_id"]

            # can't send more than 30 messages per sec, so every 20 messages,
            # we add a second
            if index % 20 == 0:
                secs += 1

            for prayer, time in prayer_times.items():
                overview_msg += f"\n<code>{prayer+':':10}{time}</code>"

                # apscheduler requires a datetime object to be passed in, so we make it here
                # slicing is done because time is provided like: "04:54 (+05)"
                prayer_time = dt.datetime.fromisoformat(today + " " + time[:5])
                seconds = dt.timedelta(seconds=secs)
                # initially, prayer time does not have a seconds value
                prayer_time += seconds

                # the Fajr reminder is different since the sunrise time has to
                # be mentioned
                if prayer == "Fajr":
                    text = (
                        "Time to pray Fajr.\nMake sure that you pray before "
                        "sunrise, which is at {}.".format(sunrise)
                    )
                else:
                    text = "Time to pray {}.".format(prayer)

                sched.add_job(
                    send_reminder,
                    "date",
                    run_date=prayer_time,
                    args=[user_id, text],
                    id=str(user_id) + "_" + prayer,
                    replace_existing=True,
                )

        # u can pick any time u want, i just wanted to use this time
        fajr_time = prayer_times["Fajr"]
        fajr_time = dt.datetime.fromisoformat(today + " " + fajr_time[:5])
        minutes = dt.timedelta(minutes=30, seconds=index)
        send_time = fajr_time - minutes

        sched.add_job(
            send_reminder,
            "date",
            run_date=send_time,
            args=[user_id, overview_msg],
            id=str(user_id) + "_overview",
            replace_existing=True,
        )

# scheduling reminders will occur every day at 2am
# 2am was picked since there are no prayers at this time
sched.add_job(schedule_all, "cron", day="*", hour=2)

