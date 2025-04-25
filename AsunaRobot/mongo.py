import asyncio
import sys
from motor import motor_asyncio
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from AsunaRobot.confing import get_int_key, get_str_key

client = MongoClient("mongodb+srv://tghcloud:Hunter01@cluster0.mzhfx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
, 27017)["AsunaRobot"]
motor = motor_asyncio.AsyncIOMotorClient("mongodb+srv://tghcloud:Hunter01@cluster0.mzhfx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
, 27017)
db = motor["AsunaRobot"]
db = client["AsunaRobot"]
try:
    asyncio.get_event_loop().run_until_complete(motor.server_info())
except ServerSelectionTimeoutError:
    sys.exit(log.critical("Can't connect to mongodb! Exiting..."))
