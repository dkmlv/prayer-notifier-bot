import csv

# ------------------------- CITIES DATA STUFF -------------------------
with open("./data/cities.csv", newline="\n") as csvfile:
    reader = csv.DictReader(csvfile)
    DATA = list(reader)

CITIES = [row["name"] for row in DATA]


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
SETUP_DONE = "Great, you are now to set to receive reminders."
PICK_OPTION = "Please choose one of the options above."

PRAYER_TIMES = "<b>{}</b>\nHere are your prayer times for today:\n\n{}"
TIME_TO_PRAY = "Time to pray {}."
SUNRISE = "Make sure that you pray before sunrise, which is at {}."
