import logging

import motor.motor_asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler as Scheduler

from data import config

client = motor.motor_asyncio.AsyncIOMotorClient("db", 27017)
db = client.prayers
cities = db.cities
users = db.users

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MongoStorage(host="db", port="27017")
dp = Dispatcher(bot, storage=storage)

sched = Scheduler(daemon=True)
sched.start()

logging.basicConfig(
    level=logging.INFO,
    format=u"%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

