from aiogram import types


async def set_default_commands(dp):
    """Set commands for the bot.

    This could have also been done directly through BotFather.
    """

    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "initial setup process"),
            types.BotCommand("help", "how to use the bot"),
            types.BotCommand("prayer_times", "get prayer times"),
            types.BotCommand("settings", "change settings"),
            types.BotCommand("cancel", "cancel current operation"),
        ]
    )
