import csv
from PIL import ImageFont

# ------------------------- DATA STUFF -------------------------
with open("./data/cities.csv", newline="\n") as csvfile:
    reader = csv.DictReader(csvfile)
    DATA = list(reader)

CITIES = [row["name"] for row in DATA]

PRAYERS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

# ------------------------- API URL -------------------------
GET_TIMES_URL = "http://api.aladhan.com/v1/calendarByCity"

# ------------------------- MESSAGES FOR THE BOT -------------------------
INTRODUCTION = (
    "As-salamu alaykum! I will remind you when it's time to pray so you "
    "never miss a prayer again!"
)
FIRST_TIME_USER = (
    "Looks like you are a first-time user.\nTo get started, can you "
    "please send me your city name?"
)
SEE_HELP = "See <b>/help</b> for more information."
ASK_PREFERENCE = "Would you like to turn on the tracking feature?"
PLEASE_WAIT = "<i><b>Please wait...</b></i>"
HELP_MESSAGE = (
    "<b>Instructions:</b>\n"
    "Once you start a chat with the bot, you should type the name of "
    "the city where you currently live. That's about it.\nYou will "
    "receive reminders at around the time of every prayer.\n\n"
    "<b>NOTE:</b> To change the city, just use the "
    "<b>/start</b> command again."
)
SEVERAL_MATCHES = "Which one of these did you mean?"
SPELLING_MISTAKE = "Did you mean one of these cities: {}?"
PICK_OPTION = "Please choose one of the options above."
SETUP_DONE = (
    "Great, you are now to set to receive reminders.\nYou can now get prayer "
    "times using <b>/prayer_times</b> command."
)
SOMETHING_WRONG = "Something went wrong. Please try <b>/start</b> again later."

PRAYER_TIMES = "<b>{}</b>\nHere are your prayer times for today:\n\n{}"
TIME_TO_PRAY = "Time to pray {}."
DID_YOU_PRAY = "Did you pray {}?"
SUNRISE = "Make sure that you pray before sunrise, which is at {}."

REGISTER_FIRST = (
    "You have not set anything up. Please use <b>/start</b> to register now."
)
OPERATION_CANCELLED = "Okay, cancelled."

# ------------------------- FONTS (PRAYER CAL) -------------------------
MONTH_FONT = ImageFont.truetype("./assets/SinkinSans-700Bold.otf", 250)
NUM_FONT = ImageFont.truetype("./assets/SinkinSans-700Bold.otf", 100)

# ------------------------- COLORS (PRAYER CAL) -------------------------
COLORS = {
    "Not Prayed": (227, 118, 114),
    "Late": (250, 206, 30),
    "Prayed": (117, 182, 184),
    "Text": (35, 40, 50),
}

# ------------------------- COORDINATES (PRAYER CAL) -------------------------
PIE_COORDINATES = {
    "Fajr": (250, 100),
    "Dhuhr": (250, 240),
    "Asr": (175, 240),
    "Maghrib": (100, 240),
    "Isha": (100, 100),
}
FIRST_MONDAY = (220, 942)
CIRCLE_COORDS = {
    "Not Prayed": 290,
    "Late": 1675,
    "Prayed": 3095,
}
