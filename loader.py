import logging
import os
import motor.motor_asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.mongo import MongoStorage

from data import config

client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
db = client.prayers
collection = db.data

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MongoStorage()
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(
    level=logging.INFO,
    format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    )

