import calendar
from difflib import get_close_matches

from aiogram import types
from aiogram.dispatcher import FSMContext

from data import (
    ASK_PREFERENCE,
    CAN_CANCEL,
    CHECK_SPREADSHEET,
    CITIES,
    DATA,
    DEMO_GIF,
    FIRST_TIME_USER,
    INTRODUCTION,
    PICK_OPTION,
    PLEASE_WAIT,
    PRAYERS,
    SEE_HELP,
    SEVERAL_MATCHES,
    SOMETHING_WRONG,
    SPELLING_MISTAKE,
    WEEKDAYS,
)
from loader import dp, tracking, users
from states import Start
from utils import get_current_dt, get_tz_info, register_user


@dp.message_handler(commands="start")
@dp.throttled(rate=3)
async def greet_user(message: types.Message):
    """Greet user, begin setup process if they are a first-time user."""
    await message.answer(INTRODUCTION)

    user = await users.find_one({"tg_user_id": message.from_user.id})

    if not user:
        await message.answer(FIRST_TIME_USER)
        await message.answer(CAN_CANCEL)
        await Start.waiting_for_city.set()
    else:
        await message.answer(SEE_HELP)


@dp.message_handler(state=Start.waiting_for_city)
async def validate_city(message: types.Message, state: FSMContext):
    """Check that user has entered a real city name.

    If only one city matches the name sent by user, ask about tracking.
    If more than one city matches, user is asked to specify their location by
    choosing one of the options.
    If nothing matches, it is assumed that user made a spelling mistake
    (we're all human) and closest matching city names are provided.
    """

    city = message.text

    matches = [
        f"{row['name']}, {row['state_name']}, {row['country_name']}"
        for row in DATA
        if row["name"].lower() == city.lower()
    ]

    if len(matches) == 1:
        await state.update_data(city=matches[0])
        await Start.waiting_for_preference.set()

        keyboard = types.InlineKeyboardMarkup()
        buttons = [
            types.InlineKeyboardButton(
                text="Yes", callback_data="tracking_on"
            ),
            types.InlineKeyboardButton(
                text="No", callback_data="tracking_off"
            ),
        ]
        keyboard.add(*buttons)

        await message.answer_animation(DEMO_GIF)
        await message.answer(ASK_PREFERENCE, reply_markup=keyboard)
    elif len(matches) > 1:
        # more than 1 city exists with that name
        await state.update_data(options=matches)
        await Start.specifying_city.set()

        options = "\n".join([f"<code>{match}</code>" for match in matches])
        await message.answer(SEVERAL_MATCHES)
        await message.answer(options)
    else:
        # probably a spelling mistake or sth
        closest_matches = get_close_matches(city.title(), CITIES)
        # marking up to make copying easier
        closest_matches = [f"<code>{m}</code>" for m in closest_matches]
        await message.answer(
            SPELLING_MISTAKE.format(", ".join(closest_matches))
        )
        await message.answer(SEVERAL_MATCHES)
        await message.answer(CHECK_SPREADSHEET, disable_web_page_preview=True)


@dp.message_handler(state=Start.specifying_city)
async def validate_specific_city(message: types.Message, state: FSMContext):
    """Check if user has chosen one of the options presented to them.

    Once the user enters a valid option, move on with setup process and ask
    about tracking.
    """

    city = message.text
    state_data = await state.get_data()
    options = state_data["options"]

    if city in options:
        await state.update_data(city=city)
        await Start.waiting_for_preference.set()

        keyboard = types.InlineKeyboardMarkup()
        buttons = [
            types.InlineKeyboardButton(
                text="Yes", callback_data="tracking_on"
            ),
            types.InlineKeyboardButton(
                text="No", callback_data="tracking_off"
            ),
        ]
        keyboard.add(*buttons)

        await message.answer_animation(DEMO_GIF)
        await message.answer(ASK_PREFERENCE, reply_markup=keyboard)
    else:
        await message.answer(PICK_OPTION)


@dp.callback_query_handler(
    text="tracking_on", state=Start.waiting_for_preference
)
async def turn_tracking_on(call: types.CallbackQuery, state: FSMContext):
    """Turn tracking on for the user.

    Create an entry for the user in the tracking collection. Move on and
    register user.
    """

    await call.answer()
    await call.message.delete_reply_markup()
    await call.message.edit_text(PLEASE_WAIT)

    tg_user_id = call.from_user.id
    state_data = await state.get_data()
    city = state_data["city"]

    tz_info = await get_tz_info(city)

    if tz_info:
        current_dt = get_current_dt(tz_info)
        current_month = current_dt.strftime("%B")

        year_num, month_num = current_dt.year, current_dt.month
        weekday, days_in_month = calendar.monthrange(year_num, month_num)

        data = {prayer: "Not Prayed" for prayer in PRAYERS}
        days = [data.copy() for _ in range(days_in_month)]

        # generate dictionary with NOT PRAYED data for each day of the month
        tracking_data = {
            "tg_user_id": tg_user_id,
            str(year_num): {
                current_month: {
                    "starts_from": WEEKDAYS[weekday],
                    "days": days,
                },
            },
        }

        await tracking.insert_one(tracking_data)

        await state.finish()
        await register_user(tg_user_id, city)
    else:
        await state.finish()
        await call.message.answer(SOMETHING_WRONG)


@dp.callback_query_handler(
    text="tracking_off", state=Start.waiting_for_preference
)
async def turn_tracking_off(call: types.CallbackQuery, state: FSMContext):
    """Turn tracking off for the user and register them."""
    await call.answer()
    await call.message.delete_reply_markup()
    await call.message.edit_text(PLEASE_WAIT)

    tg_user_id = call.from_user.id
    state_data = await state.get_data()
    city = state_data["city"]

    await state.finish()
    await register_user(tg_user_id, city)
