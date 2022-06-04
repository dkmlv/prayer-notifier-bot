import logging

from aiogram import Dispatcher
from data.config import ADMIN


async def notify_on_startup(dp: Dispatcher):
    """Notify admin that the bot has launched."""
    try:
        await dp.bot.send_message(ADMIN, "Bot launched!")
    except Exception as err:
        logging.exception(err)


async def notify_on_shutdown(dp: Dispatcher):
    """Notify admin that the bot has shut down."""
    try:
        await dp.bot.send_message(ADMIN, "Bot shut down!")
    except Exception as err:
        logging.exception(err)
