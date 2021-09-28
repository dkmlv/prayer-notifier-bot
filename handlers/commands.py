import logging
import pprint

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from loader import collection, db, dp
# from states.all_states import SetupStates

setup_in_progress = State()

@dp.message_handler(commands="start", state="*")
async def welcome_user(message: types.Message, state: FSMContext):
    """
    Sends a welcome greeting to the user with a brief explanation of what the
    bot does. Suggests the user to send the `/setup` command (see below).
    """
    await state.finish()
    await message.reply("Whatever, hello. Send `/setup`.")


@dp.message_handler(commands="setup")
async def ask_location(message: types.Message, state: FSMContext):
    """
    Asks the user to type the city they live in rn. This will be needed for the
    API requests.
    """
    await message.reply("Which city do you live in?")

    await setup_in_progress.set()
    # await SetupStates.waiting_for_city.set()


@dp.message_handler(state=setup_in_progress, regexp="city")
async def ask_notification_time(message: types.Message, state: FSMContext):
    """
    Asks the user when they would like to be notified.
    """
    await state.update_data(city=message.text) 

    await message.reply("When would you like to be notified?")


@dp.message_handler(state=setup_in_progress, regexp="mins")
async def add_user(message: types.Message, state: FSMContext):
    """
    Adds the user to the database.
    """
    data = await state.get_data()
    city_name = data["city"]
    print(city_name)
    notification_time = message.text
    print(notification_time)

    await state.finish()

    document = await collection.find_one({"city": city_name})
    print(document)
    pprint.pprint(document)

    if document is None:
        print("yo")
        user_data = {
                "city": city_name,
                "users": {
                    str(message.from_user.id): notification_time
                    }
                }
        await collection.insert_one(user_data)
    else:
        print ("how")



