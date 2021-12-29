"""A simple GET request to the prayer times API."""

import datetime as dt
import logging

import requests


async def get_prayer_times(city_name):
    """Return prayer times for today for a certain city."""
    today = dt.date.today()

    day = today.day
    month = today.month
    year = today.year

    parameters = {
        "city": city_name,
        "country": "Uzbekistan",
        "school": 1,
        "method": 3,
        "month": month,
        "year": year,
    }

    try:
        response = requests.get(
            "http://api.aladhan.com/v1/calendarByCity", params=parameters
        )
    except requests.exceptions.RequestException:
        logging.exception("Failed to get a response from the API.")
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

    return times
