from aiogram import executor

import middlewares
import handlers
from loader import dp, sched
from utils.notify_admin import notify_on_startup
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    """
    Sets default commands for the bot and notifies the admin of bot startup.
    """
    await set_default_commands(dispatcher)
    await notify_on_startup(dispatcher)


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
