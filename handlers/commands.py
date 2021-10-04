import logging
import datetime as dt

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State

from loader import cities, dp, sched, users
from handlers.schedule_messages import schedule_one


setup_in_progress = State()


@dp.message_handler(commands="start")
async def ask_location(message: types.Message):
    """
    Asks the user to type the city they live in rn. This will be needed for the
    GET requests and scheduling sending the message.
    """
    await message.reply(
        "Hello! Please send me the name of the city where you live "
        "and you will be set."
    )

    await setup_in_progress.set()


@dp.message_handler(commands="help", state="*")
async def give_help(message: types.Message):
    """
    Provides some instructions on how to use the bot to the user + brief info.
    """
    await message.reply(
        "<b>Instructions:</b>\n"
        "Once you start a chat with the bot, you should type the name of "
        "the city where you currently live. That's about it.\nYou will "
        "receive reminders around 5 minutes before each prayer.\n\n"
        "<b>Additional:</b> To change the city, just use the "
        "<b><i>/start</i></b> command again."
    )


@dp.message_handler(state=setup_in_progress)
async def add_user(message: types.Message, state: FSMContext):
    """
    Adds the user to the database.
    """
    city_name = message.text
    user_id = message.from_user.id

    document = await cities.find_one({"city": city_name})

    # if the city odes not already exist in the cities collection
    if document is None:
        # make a get request to the prayer times api, get the prayer times
        # for this city
        parameters = {"city": city_name, "juristic": 1}
        response = requests.get(
            "https://api.pray.zone/v2/times/today.json", params=parameters
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
        times = response["results"]["datetime"][0]["times"]

        await cities.insert_one(
            {"city": city_name, "times": times}
        )

    user_data = {"user_id": user_id, "city": city_name}
    await users.update_one({"user_id": user_id}, {"$set": user_data}, upsert=True)

    await message.reply("All right, the setup is done.")

    await schedule_one(message)

    await state.finish()
