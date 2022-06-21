[![GitHub](https://img.shields.io/github/license/DurbeKK/prayer-notifier-bot)](https://github.com/DurbeKK/prayer-notifier-bot/blob/main/LICENSE) [![Telegram](https://img.shields.io/badge/telegram-%40prayersTgBot-blue)](https://t.me/prayersTgBot)

# Prayer Notifier Bot

This is a very simple notifier bot that reminds you to pray at around the time
of the prayer. Bot works in all timezones and can also track prayers.

To obtain the prayer times, [this API](https://aladhan.com/prayer-times-api) is used.
To obtain the hijri date, [this package](https://hijri-converter.readthedocs.io/en/stable/index.html) is used.

## Installation

Change the variables in the `.env.example` file and then rename the file to `.env`.
Next, build an image using the Dockerfile and then run your bot. That's about it.
