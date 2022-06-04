"""Handler for the /start command."""

from difflib import get_close_matches

from aiogram import types
from aiogram.dispatcher import FSMContext

from data.constants import (
    CITIES,
    DATA,
    FIRST_TIME_USER,
    INTRODUCTION,
    PICK_OPTION,
    SEE_HELP,
    SETUP_DONE,
    SEVERAL_MATCHES,
    SPELLING_MISTAKE,
)
from loader import dp, users
from states.all_states import Start
from utils.user import register_user


@dp.message_handler(commands="start")
async def greet_user(message: types.Message):
    """Greet user, ask for their location if they are a first-time user."""
    await message.answer(INTRODUCTION)

    user = await users.find_one({"tg_user_id": message.from_user.id})

    if not user:
        await message.answer(FIRST_TIME_USER)
        await Start.waiting_for_city.set()
    else:
        await message.answer(SEE_HELP)


@dp.message_handler(state=Start.waiting_for_city)
async def validate_city(message: types.Message, state: FSMContext):
    """Check that user has entered a real city name.

    If only one city matches the name sent by user, the new user is registered.
    If more than one city matches, user is asked to specify their location by
    choosing one of the options.
    If nothing matches, it is assumed that user made a spelling mistake
    (we're all human) and closest matching city names are provided.
    """

    city = message.text.capitalize()

    matches = [
        f"{city}, {row['state_name']}, {row['country_name']}"
        for row in DATA
        if row["name"] == city
    ]

    if len(matches) == 1:
        await state.finish()
        await register_user(message.from_user.id, matches[0])
        await message.answer(SETUP_DONE)
    elif len(matches) > 1:
        # more than 1 city exists with that name
        await state.update_data(options=matches)
        await Start.specifying_city.set()

        options = "\n".join([f"<code>{match}</code>" for match in matches])
        await message.answer(SEVERAL_MATCHES)
        await message.answer(options)
    else:
        # probably a spelling mistake or sth
        closest_matches = get_close_matches(city, CITIES)
        # marking up to make copying easier
        closest_matches = [f"<code>{m}</code>" for m in closest_matches]
        await message.answer(
            SPELLING_MISTAKE.format(", ".join(closest_matches))
        )
        await message.answer(SEVERAL_MATCHES)


@dp.message_handler(state=Start.specifying_city)
async def validate_specific_city(message: types.Message, state: FSMContext):
    """Check if user has chosen one of the options presented to them.

    Once the user enters a valid option, register the new user to recieve
    reminders to pray.
    """

    city = message.text
    state_data = await state.get_data()
    options = state_data["options"]

    if city in options:
        await state.finish()
        await register_user(message.from_user.id, city)
        await message.answer(SETUP_DONE)
    else:
        await message.answer(PICK_OPTION)
