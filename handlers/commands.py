from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State

from handlers.schedule_messages import schedule_one
from loader import cities, dp, users
from utils.get_prayer_times import get_prayer_times
from utils.hijri_date import get_todays_hijri_date

setup_in_progress = State()


@dp.message_handler(commands="start")
async def ask_location(message: types.Message):
    """Ask the user to type the city they live in rn.

    This will be needed for the GET requests and scheduling the message.
    """

    await message.reply(
        "Hello! Please send me the name of the city where you live "
        "and you will be set.\n\n<b>NOTE:</b> currently, the bot only works "
        "in Uzbekistan."
    )

    await setup_in_progress.set()


@dp.message_handler(commands="help", state="*")
async def give_help(message: types.Message):
    """Provide some instructions on how to use the bot + brief info."""
    await message.reply(
        "<b>Instructions:</b>\n"
        "Once you start a chat with the bot, you should type the name of "
        "the city where you currently live. That's about it.\nYou will "
        "receive reminders at around the time of every prayer.\n\n"
        "<b>NOTE:</b> To change the city, just use the "
        "<b>/start</b> command again."
    )


@dp.message_handler(state=setup_in_progress)
async def add_user(message: types.Message, state: FSMContext):
    """Add the user to database. Schedule reminders for new user for today."""
    city_name = message.text
    user_id = message.from_user.id

    document = await cities.find_one({"city": city_name})

    if not document:
        prayer_times = await get_prayer_times(city_name)

        hijri_date = get_todays_hijri_date()

        await cities.insert_one(
            {
                "city": city_name,
                "times": prayer_times,
                "hijri_date": hijri_date,
            }
        )

    user_data = {"user_id": user_id, "city": city_name}
    await users.update_one({"user_id": user_id}, {"$set": user_data}, upsert=True)

    await message.reply(
        "Great, you're all set. You should now receive reminders at about the "
        "time of every prayer."
    )

    await state.finish()

    await schedule_one(message)


@dp.message_handler(state=None)
async def another_help_message(message: types.Message):
    """Ask the user to type help to get more info.

    This function will be called when the user types a random message.
    """

    await message.reply("See <code>/help</code> for more information.")
