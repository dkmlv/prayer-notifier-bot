import logging

import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler as Scheduler

from data import config

uri = "mongodb+srv://{}:{}@{}/prayers?retryWrites=true&w=majority".format(
    config.DB_USER,
    config.DB_PASSWORD,
    config.DB_HOST,
)
client = AsyncIOMotorClient(uri)
db = client.prayers

# mongodb collections
cities = db.cities
users = db.users

session = aiohttp.ClientSession()

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

fsm_uri = (
    "mongodb+srv://{}:{}@{}/aiogram_fsm?retryWrites=true&w=majority".format(
        config.DB_USER, config.DB_PASSWORD, config.DB_HOST
    )
)
storage = MongoStorage(uri=fsm_uri)

dp = Dispatcher(bot, storage=storage)

sched = Scheduler(daemon=True)
sched.start()

logging.basicConfig(
    level=logging.INFO,
    format=u"%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
