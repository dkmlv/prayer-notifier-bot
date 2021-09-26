from aiogram import types

async def set_default_commands(dp):
    """
    Sets commands for the bot.
    (This could have also been done directly through BotFather)
    """
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "about info"),
            types.BotCommand("help", "how to use the bot"),
            types.BotCommand("merge", "merge PDF files"),
            types.BotCommand("compress", "compress PDF file"),
            types.BotCommand("encrypt", "encrypt PDF file"),
            types.BotCommand("decrypt", "decrypt PDF file"),
            types.BotCommand("split", "extract pages from your PDF"),
            types.BotCommand("convert", "convert Word/Images to PDF"),
            types.BotCommand("cancel", "cancel current operation"),
        ]
    )