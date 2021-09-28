import logging
import pprint

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from loader import dp, cities, users

setup_in_progress = State()


@dp.message_handler(commands="start")
async def ask_location(message: types.Message, state: FSMContext):
    """
    Asks the user to type the city they live in rn. This will be needed for the
    API requests.
    """
    await message.reply("Which city do you live in?")

    await setup_in_progress.set()


@dp.message_handler(state=setup_in_progress)
async def add_user(message: types.Message, state: FSMContext):
    """
    Adds the user to the database.
    """
    city_name = message.text
    user_id = message.from_user.id

    document = await cities.find_one({"city": city_name})
    pprint.pprint(document)

    # if the city odes not already exist in the cities collection
    if document is None:
        # TODO: make a get request to the prayer times api, get the prayer times
        # for this city
        parameters = {"city": city_name}
        response = requests.get(
            "https://api.pray.zone/v2/times/today.json", params=parameters
        )

        # checking if the city is actually avaialble in the api
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            await message.reply(
                "Sorry, the prayer times for that city are unavailable."
                "Try typing in another city."
            )
            return

        response = response.json()
        times = response["results"]["datetime"][0]["times"]
        offset = response["results"]["location"]["local_offset"]

        await cities.insert_one({
            "city": city_name,
            "times": times,
            "time_offset": offset
            })

    user_data = {"user_id": user_id, "city": city_name}
    await users.update_one({"user_id": user_id}, {"$set": user_data}, upsert=True)

    await message.reply("IT WORKED")
    await state.finish()
