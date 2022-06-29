import csv

from PIL import ImageFont
from aiogram.utils.emoji import emojize

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
    f"<b>Never miss a prayer again!</b> {emojize(':clock8:')}\nI will remind "
    "you when it's time to pray and can help you keep track of your prayers.\n"
    f"\n<b>Commands</b> {emojize(':speech_balloon:')}\n"
    "<i>/start</i> - initial setup process\n"
    "<i>/help</i> - detailed info on commands and extra notes\n"
    "<i>/prayer_times</i> - get prayer times for the day (will send tomorrow's"
    " prayer times if there are no prayers left for today)\n"
    "<i>/settings</i> - change user settings (resetting all settings will "
    "erase all user data and start the initial setup process)\n"
    "<i>/cancel</i> - cancel current operation (if you feel like everything "
    "is frozen, try running this command)\n\n"
    "<b>NOTE:</b> the bot uses <i>Hanafi</i> school of thought.\n\n"
    "If you encounter any issues, please reach out to @whereismyxanax\n"
    "<a href='https://www.buymeacoffee.com/dkamolov'>Buy me a coffee</a> "
    f"{emojize(':coffee:')}"
)
SEVERAL_MATCHES = "Which one of these did you mean?"
SPELLING_MISTAKE = "Did you mean one of these cities: {}?"
PICK_OPTION = "Please choose one of the options above."
SETUP_DONE = (
    "Great, you are now to set to receive reminders. You can get prayer times "
    "using <b>/prayer_times</b> command."
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
NOTED = "Noted, thank you!"

CAN_CANCEL = "You can cancel this operation anytime using <b>/cancel</b>."
CHECK_SPREADSHEET = (
    "If you can't seem to find your region, try checking that it exists <a "
    "href='https://docs.google.com/spreadsheets/d/1SRmeEf3S4APZInjxnMjUft5kWhP"
    "r2MwP0_Ya6NwZAyA/edit?usp=sharing'>here</a>."
)

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
    "Not Prayed": 325,
    "Late": 1710,
    "Prayed": 3110,
}

# ------------------------- DEMO GIF FILE ID -------------------------
DEMO_GIF = (
    "CgACAgIAAxkBAAJMYmKxrb28qDBOHBH1i6Hj-oG0M_tQAAKXGwACnUqISeM0b-AfHynZKQQ"
)
