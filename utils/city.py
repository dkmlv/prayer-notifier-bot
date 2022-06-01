from loader import cities


async def setup_city(city: str):
    """Get prayer times for the city and set up automatic updating.

    1. Get timezone information for the city.
    2. Get prayer times for today (the day is determined using timezone info)
        - If any prayers are left for today, insert today's prayer times to DB.
        - Else get tomorrow's prayer times and insert them to DB.
    3. Schedule a job to run 15 minutes after the last prayer of the day. The
    job will get the next day's prayer times for that city and schedule
    reminders for all users who chose that city.

    Parameters
    ----------
    city : str
        New user's location, looks sth like: "Springfield, CO, US"
    """

    pass


async def process_city(city: str):
    """Process city information.

    Check whether city exists in DB and set it up if it doesn't.

    Parameters
    ----------
    city : str
        New user's location, looks sth like: "Springfield, CO, US"
    """

    document = cities.find_one({"city": city})

    if not document:
        await setup_city(city)
