import asyncio
import calendar
import datetime as dt
import logging
import operator
import os
from typing import Dict

from PIL import Image, ImageDraw
from aiogram import exceptions, types

from data import (
    CIRCLE_COORDS,
    COLORS,
    FIRST_MONDAY,
    MONTH_FONT,
    NUM_FONT,
    PIE_COORDINATES,
    PRAYERS,
    WEEKDAYS,
)
from loader import bot, tracking
from utils import cleanup_user, get_current_dt


def generate_pie_chart(data: Dict[str, str]) -> Image.Image:
    """Generate a pie chart with the provided user data.

    Parameters
    ----------
    data : Dict[str, str]
        User data obtained from the tracking collection

    Returns
    -------
    Image.Image
        Pillow Image object
    """

    with Image.open("./assets/pie-no-colors.png") as pie_chart:
        pie_chart = pie_chart.convert("RGB")

        for key, value in data.items():
            coordinate, color = PIE_COORDINATES[key], COLORS[value]
            ImageDraw.floodfill(pie_chart, coordinate, color)

        prayers_img = Image.open("./assets/prayers_text.png").convert("RGBA")
        pie_chart.paste(prayers_img, (0, 0), prayers_img)
        prayers_img.close()

        return pie_chart


async def generate_prayer_calendar(tg_user_id: int, tz_info: str, data: dict):
    """Generate a prayer calendar for the user.

    Parameters
    ----------
    tg_user_id : int
        Telegram user id
    tz_info : str
        Timezone information string, like "Europe/Rome"
    data : dict
        User's prayer data (a single document from mongodb)
    """

    now = get_current_dt(tz_info)
    days_ago = now - dt.timedelta(days=5)
    last_month_name, year = days_ago.strftime("%B"), str(days_ago.year)

    last_month_data = data[year][last_month_name]
    starts_from, days = last_month_data["starts_from"], last_month_data["days"]
    num_of_days = len(days)

    if starts_from == "Monday" and num_of_days == 28:
        rows = 4
    elif (starts_from == "Sunday" and num_of_days in (30, 31)) or (
        starts_from == "Saturday" and num_of_days == 31
    ):
        rows = 6
    else:
        rows = 5

    with Image.open(f"./assets/calendar-{rows}.png") as calendar_img:
        calendar_img = calendar_img.convert("RGB")
        ImageDraw.Draw(calendar_img).text(
            (350, 265), last_month_name, COLORS["Text"], MONTH_FONT
        )

        prayers = {"Prayed": 0, "Not Prayed": 0, "Late": 0}
        start = WEEKDAYS.index(starts_from)

        for index, day in enumerate(days, start=start):
            pie_chart_img = generate_pie_chart(day)

            for key in prayers:
                prayers[key] += operator.countOf(day.values(), key)

            x = FIRST_MONDAY[0] + index % 7 * 551
            y = FIRST_MONDAY[1] + index // 7 * 400
            calendar_img.paste(pie_chart_img, (x, y))

        for key in prayers:
            percentage = str(round(prayers[key] / (5 * num_of_days) * 100))
            offset = (len(percentage) - 1) * 35

            ImageDraw.Draw(calendar_img).text(
                (CIRCLE_COORDS[key] - offset, calendar_img.height - 440),
                f"{percentage}%",
                COLORS["Text"],
                NUM_FONT,
            )

        calendar_img.save(f"./temp/{tg_user_id}.png")


async def send_photo(tg_user_id: int, image_path: str, caption: str):
    """Safe photo sender.

    Parameters
    ----------
    user_id : int
        Telegram user id
    image_path : str
        The path to the image that needs to be sent
    caption : str
        The caption to send with the image
    """

    try:
        await bot.send_photo(
            tg_user_id, types.InputFile(image_path), caption=caption
        )
    except exceptions.BotBlocked:
        logging.error(f"Target [ID:{tg_user_id}]: blocked by user")
        await cleanup_user(tg_user_id)
    except exceptions.ChatNotFound:
        logging.error(f"Target [ID:{tg_user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logging.error(
            f"Target [ID:{tg_user_id}]: Flood limit is exceeded. "
            f"Sleep {e.timeout} seconds."
        )
        await asyncio.sleep(e.timeout)
        # Recursive call
        return await send_photo(tg_user_id, image_path, caption)
    except exceptions.UserDeactivated:
        logging.error(f"Target [ID:{tg_user_id}]: user is deactivated")
        await cleanup_user(tg_user_id)
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{tg_user_id}]: failed")
    else:
        logging.info(f"Target [ID:{tg_user_id}]: success")


async def send_prayer_calendar(tg_user_id: int, tz_info: str):
    """Send the prayer calendar to the user.

    Parameters
    ----------
    tg_user_id : int
        Telegram user id
    tz_info : str
        Timezone information string, like "Europe/Rome"
    """

    data = await tracking.find_one({"tg_user_id": tg_user_id})
    await generate_prayer_calendar(tg_user_id, tz_info, data)

    caption = (
        "Here is your prayer calendar for the last month!\n"
        "<b>NOTE:</b> percentages may not add up to 100 due to rounding."
    )
    calendar_img_path = f"./temp/{tg_user_id}.png"

    await send_photo(tg_user_id, calendar_img_path, caption)

    os.remove(calendar_img_path)

    # generate dictionary with NOT PRAYED data for each day of the new month
    current_dt = get_current_dt(tz_info)
    current_month = current_dt.strftime("%B")

    year_num, month_num = current_dt.year, current_dt.month
    weekday, days_in_month = calendar.monthrange(year_num, month_num)

    data = {prayer: "Not Prayed" for prayer in PRAYERS}
    days = [data.copy() for _ in range(days_in_month)]

    new_month_data = {
        "starts_from": WEEKDAYS[weekday],
        "days": days,
    }
    await tracking.update_one(
        {"tg_user_id": tg_user_id},
        {"$set": {f"{year_num}.{current_month}": new_month_data}},
    )
