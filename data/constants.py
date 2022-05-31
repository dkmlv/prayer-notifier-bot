import csv

# ------------------------- CITIES DATA STUFF -------------------------
with open("./data/cities.csv", newline="\n") as csvfile:
    reader = csv.DictReader(csvfile)
    DATA = list(reader)

CITIES = [row["name"] for row in DATA]

# ------------------------- MESSAGES FOR THE BOT -------------------------
INTRODUCTION = "Hello, I will help you with blah blah blah."
FIRST_TIME_USER = (
    "Looks like you are a first-time user.\nTo get started, can you "
    "please send me your city name?"
)
HELP_MESSAGE = (
    "<b>Instructions:</b>\n"
    "Once you start a chat with the bot, you should type the name of "
    "the city where you currently live. That's about it.\nYou will "
    "receive reminders at around the time of every prayer.\n\n"
    "<b>NOTE:</b> To change the city, just use the "
    "<b>/start</b> command again."
)
SEE_HELP = "See <b>/help</b> for more information."

# ------------------------- STICKER FILE IDS -------------------------
HI_STICKER = (
    "CAACAgIAAxkBAAEBG6xik1mL3a1-ewaOpplo8tbVntFZMAACVAADQbVWDGq3-McIjQH6JAQ"
)
