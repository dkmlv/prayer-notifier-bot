from aiogram import executor

import handlers
from loader import dp, session, sched
from utils.notify_admin import notify_on_shutdown, notify_on_startup
from utils.set_bot_commands import set_default_commands
from utils.recreate_jobs import recreate_jobs


async def on_startup(dispatcher):
    """Set default commands for the bot and notify of bot startup."""
    await set_default_commands(dispatcher)
    await notify_on_startup(dispatcher)
    sched.start()
    await recreate_jobs()


async def on_shutdown(dispatcher):
    """Close connections and notify of bot shutdown."""
    await session.close()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    await notify_on_shutdown(dispatcher)


if __name__ == "__main__":
    executor.start_polling(
        dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True
    )
