import logging

import motor.motor_asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler as Scheduler

from data import config

uri = "mongodb://{}:{}@{}:{}".format(
    config.DB_USER, config.DB_PSSWD, config.HOST, config.PORT
)
client = motor.motor_asyncio.AsyncIOMotorClient(uri)
db = client.prayers
cities = db.cities
users = db.users

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MongoStorage(
    host=config.HOST,
    port=config.PORT,
    db_name="aiogram_fsm",
    username=config.DB_USER,
    password=config.DB_PSSWD,
)
dp = Dispatcher(bot, storage=storage)

sched = Scheduler(daemon=True)
sched.start()

logging.basicConfig(
    level=logging.INFO,
    format=u"%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

