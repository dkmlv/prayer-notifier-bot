from aiogram import Dispatcher, executor

import handlers
from loader import dp, sched, session
from utils import (
    notify_on_shutdown,
    notify_on_startup,
    recreate_jobs,
    set_default_commands,
)


async def on_startup(dispatcher: Dispatcher):
    """Operations to perform on startup."""
    await set_default_commands(dispatcher)
    await notify_on_startup(dispatcher)
    sched.start()
    await recreate_jobs()


async def on_shutdown(dispatcher: Dispatcher):
    """Operations to perform on shutdown."""
    await session.close()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    await notify_on_shutdown(dispatcher)
    sched.shutdown()


if __name__ == "__main__":
    executor.start_polling(
        dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True
    )
