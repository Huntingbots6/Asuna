# HuntingBots

import asyncio
import sys
import logging as log

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from AsunaRobot import MONGO_DB_URI
from AsunaRobot.services.setup import get_int_key, get_str_key


MONGO_PORT = get_int_key("27017")
MONGO_DB_URI = get_str_key("MONGO_DB_URI")
MONGO_DB = "AsunaRobot"


# MongoDB client
log.info("Initializing MongoDB client")
mongo_client = MongoClient(MONGO_URL)
db = mongo_client.AsunaRobot
try:
    asyncio.get_event_loop().run_until_complete(motor.server_info())
except ServerSelectionTimeoutError:
    sys.exit(log.critical("Can't connect to mongodb! Exiting..."))
