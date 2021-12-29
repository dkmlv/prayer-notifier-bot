[![GitHub](https://img.shields.io/github/license/DurbeKK/prayer-notifier-bot)](https://github.com/DurbeKK/prayer-notifier-bot/blob/main/LICENSE) [![Telegram](https://img.shields.io/badge/telegram-%40prayersTgBot-blue)](https://t.me/prayersTgBot)

# Prayer Notifier Bot

This is a very simple notifier bot that reminds you to pray at around the time
of the prayer. Currently the bot only works in the +5 timezone because I was
too dumb to dumb to figure out how to design it so that it would work
everywhere.

## Current Implementation

As mentioned above, this is a very basic bot. Reminders are scheduled every day
at 2am.

To obtain the prayer times, the following API is used:
https://aladhan.com/prayer-times-api

To obtain the hijri date, the following package is used:
https://hijri-converter.readthedocs.io/en/stable/index.html

## Installation

Change the variables in the .env.example file and then rename the file to .env.
Then just run the following in your terminal:

```sh
docker-compose up -d
```

