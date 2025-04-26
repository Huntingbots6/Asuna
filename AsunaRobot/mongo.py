# Made For AsunaRobot

import asyncio
import sys
from motor import motor_asyncio
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

client = MongoClient("mongodb+srv://huntingbots:huntingbots00@cluster0.8w0fe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
, 27017)["AsunaRobot"]
motor = motor_asyncio.AsyncIOMotorClient("mongodb+srv://huntingbots:huntingbots00@cluster0.8w0fe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
, 27017)
db = motor["AsunaRobot"]
db = client["AsunaRobot"]
try:
    asyncio.get_event_loop().run_until_complete(motor.server_info())
except ServerSelectionTimeoutError:
    sys.exit(log.critical("Can't connect to mongodb! Exiting..."))
