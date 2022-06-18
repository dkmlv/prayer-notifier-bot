import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.mongo import MongoStorage
import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler as Scheduler
from motor.motor_asyncio import AsyncIOMotorClient

from data import BOT_TOKEN, DB_HOST, DB_PASSWORD, DB_USER

uri = "mongodb+srv://{}:{}@{}/prayers?retryWrites=true&w=majority".format(
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
)
client = AsyncIOMotorClient(uri)
db = client.prayers

# mongodb collections
cities = db.cities
users = db.users
tracking = db.tracking

session = aiohttp.ClientSession()

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)

fsm_uri = (
    "mongodb+srv://{}:{}@{}/aiogram_fsm?retryWrites=true&w=majority".format(
        DB_USER, DB_PASSWORD, DB_HOST
    )
)
storage = MongoStorage(uri=fsm_uri)

dp = Dispatcher(bot, storage=storage)

sched = Scheduler(daemon=True)

logging.basicConfig(
    level=logging.INFO,
    format=u"%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
