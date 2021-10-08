import datetime as dt
import logging

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from handlers.schedule_messages import schedule_one
from loader import cities, dp, users

class OnlyState(StatesGroup):
    setup_in_progress = State()


@dp.message_handler(commands="start")
async def ask_location(message: types.Message):
    """
    Asks the user to type the city they live in rn. This will be needed for the
    GET requests and scheduling sending the message.
    """
    await message.reply(
        "Hello! Please send me the name of the city where you live "
        "and you will be set.\n\n<b>NOTE:</b> currently, the bot only works "
        "in Uzbekistan."
    )

    await OnlyState.setup_in_progress.set()


@dp.message_handler(commands="help", state="*")
async def give_help(message: types.Message):
    """
    Provides some instructions on how to use the bot to the user + brief info.
    """
    await message.reply(
        "<b>Instructions:</b>\n"
        "Once you start a chat with the bot, you should type the name of "
        "the city where you currently live. That's about it.\nYou will "
        "receive reminders at around the time of every prayer.\n\n"
        "<b>Additional:</b> To change the city, just use the "
        "<b><code>/start</code></b> command again."
    )


@dp.message_handler(state=OnlyState.setup_in_progress)
async def add_user(message: types.Message, state: FSMContext):
    """
    Adds the user to the database. Schedules reminders for new user for today.
    """
    city_name = message.text
    user_id = message.from_user.id

    document = await cities.find_one({"city": city_name})

    today = dt.date.today()

    day = today.day
    month = today.month
    year = today.year

    if document is None:
        parameters = {
            "city": city_name,
            "country": "Uzbekistan",
            "school": 1,
            "method": 3,
            "month": month,
            "year": year,
        }
        response = requests.get(
            "http://api.aladhan.com/v1/calendarByCity", params=parameters
        )

        # checking if the city is actually avaialble in the api
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            await message.reply(
                "Sorry, the prayer times for that city are unavailable. "
                "Try typing in another city.\n\n"
                "You can see if your city is available here:\n"
                "https://prayertimes.date/api/docs/cities"
            )
            return

        response = response.json()

        today_data = response["data"][day - 1]
        times = today_data["timings"]

        not_needed = ["Imsak", "Sunset", "Midnight"]
        for item in not_needed:
            times.pop(item)

        for prayer, time in times.items():
            # slicing is done because time is provided like: "04:54 (+05)"
            times[prayer] = time[:5]

        hijri_data = today_data["date"]["hijri"]
        h_day = hijri_data["day"]
        h_month = hijri_data["month"]["en"]
        h_year = hijri_data["year"]
        h_designation = hijri_data["designation"]["abbreviated"]

        hijri_date = f"<b>{h_day} {h_month} {h_year} {h_designation}</b>\n"

        await cities.insert_one(
            {
                "city": city_name,
                "times": times,
                "hijri_date": hijri_date,
            }
        )

    user_data = {"user_id": user_id, "city": city_name}
    await users.update_one({"user_id": user_id}, {"$set": user_data}, upsert=True)

    await message.reply("All right, the setup is done.")

    await state.finish()

    await schedule_one(message)



@dp.message_handler(state=None)
async def another_help_message(message: types.Message):
    """
    Will ask the user to type help to get more info.
    This function will be called when the user types a random message or
    message.
    """
    await message.reply("See <code>/help</code> for more information.")

