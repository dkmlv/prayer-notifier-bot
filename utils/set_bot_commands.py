from aiogram import types

async def set_default_commands(dp):
    """
    Sets commands for the bot.
    (This could have also been done directly through BotFather)
    """
    await dp.bot.set_my_commands(
        [
            types.BotCommand("settings", "change user settings"),
            types.BotCommand("help", "how to use the bot"),
        ]
    )
