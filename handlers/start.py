from difflib import get_close_matches

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.constants import (
    CITIES,
    DATA,
    FIRST_TIME_USER,
    HI_STICKER,
    INTRODUCTION,
    SEE_HELP,
)
from loader import dp


class Start(StatesGroup):
    waiting_for_city = State()


@dp.message_handler(commands="start")
async def greet_user(message: types.Message):
    """Greet user and ask their location if they don't exist in db."""
    await message.answer_sticker(HI_STICKER)
    await message.answer(INTRODUCTION)

    # TODO: Check if user is in DB
    user = 0

    if not user:
        await message.answer(FIRST_TIME_USER)
        await Start.waiting_for_city.set()
    else:
        await message.answer(SEE_HELP)


@dp.message_handler(state=Start.waiting_for_city)
async def validate_city(message: types.Message, state: FSMContext):
    """Check that user has entered a real city name."""
    city = message.text

    matches = CITIES.count(city)

    if matches == 1:
        await message.answer("Success, only 1 city found.")
    elif matches > 1:
        # same city name, different places
        choices = ""
        for row in DATA:
            if row["name"] == city:
                state_n = row["state_name"]
                country = row["country_name"]
                choices += f"<code>{city}, {state_n}, {country}</code>\n"

        await message.answer("Which one of these did you mean?")
        await message.answer(choices)
    else:
        closest_matches = get_close_matches(city, CITIES)
        await message.answer(
            f"Did you mean one of these cities: "
            f"<code>{', '.join(closest_matches)}</code>?"
        )

    await state.finish()
