# Create a new config.py or rename this to config.py file in same dir and import, then extend this class.
import json
import os


def get_user_list(config, key):
    with open("{}/AsunaRobot/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]


# Create a new config.py or rename this to config.py file in same dir and import, then extend this class.
class Config(object):
    LOGGER = True
    # REQUIRED
    # Login to https://my.telegram.org and fill in these slots with the details given by it

    API_ID = "3975570"  # integer value, dont use ""
    API_HASH = "680b62f2844aa1954216f6cb99d2f3d9"
    TOKEN = "1843295508:AAFW5BZHxlB9B72xVj-rraTBMFa7BOVd8b4"  # This var used to be API_KEY but it is now TOKEN, adjust accordingly.
    OWNER_ID = 1606221784  # If you dont know, run the bot and do /id in your private chat with it, also an integer
    OWNER_USERNAME = "The_Ghost_Hunter"
    SUPPORT_CHAT = "AsunaRobotSupport"  # Your own group for support, do not add the @
    JOIN_LOGGER = (
        -1001432609692
    )  # Prints any new group the bot is added to, prints just the name and ID.
    EVENT_LOGS = (
        -1001432768300
    )  # Prints information like gbans, sudo promotes, AI enabled disable states that may help in debugging and shit

    # RECOMMENDED
    WEBHOOK = ""
    URL = ""
    PORT = ""
    CERT_PATH = ""
    

    DATABASE_URL = "postgresql://tghbot_owner:npg_jae9mlh4kOMN@ep-shy-feather-a4hofch2-pooler.us-east-1.aws.neon.tech/tghbot?sslmode=require"
    MONGO_DB_URI = "mongodb+srv://huntingbots:huntingbots00@cluster0.8w0fe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    ARQ_API_KEY = "QVFHGP-ARXCNX-STOXKZ-DGMLRU-ARQ"
    ARQ_API_URL = "https://thearq.tech"
    DONATION_LINK = ""
    LOAD = ""
    TEMP_DOWNLOAD_DIRECTORY = ""
    OPENWEATHERMAP_ID = ""
    NO_LOAD = ""
    HEROKU_API_KEY = ""
    HEROKU_APP_NAME = ""
    DEL_CMDS = ""
    STRICT_GBAN = ""
    WORKERS = ""
    BAN_STICKER = ""
    ALLOW_CHATS = ""
    ALLOW_EXCL = ""
    CASH_API_KEY = ""
    TIME_API_KEY = ""
    WALL_API = ""
    SPAMWATCH_API = "4K~uuKGR_Ntet64M_cvsc4HoMvnq6sH821AfprRrGfF6aFQL2FbxRQN64CHkYY9L"  # go to support.spamwat.ch to get key
    SPAMWATCH_SUPPORT_CHAT = "@SpamWatchSupport"
    INFOPIC = "True"
    OPENAI_API_KEY = ""
    LASTFM_API_KEY = ""
    CF_API_KEY = ""

    
    # OPTIONAL
    ##List of id's -  (not usernames) for users which have sudo access to the bot.
    DRAGONS = get_user_list("elevated_users.json", "sudos")
    ##List of id's - (not usernames) for developers who will have the same perms as the owner
    DEV_USERS = get_user_list("elevated_users.json", "devs")
    ##List of id's (not usernames) for users which are allowed to gban, but can also be banned.
    DEMONS = get_user_list("elevated_users.json", "supports")
    # List of id's (not usernames) for users which WONT be banned/kicked by the bot.
    TIGERS = get_user_list("elevated_users.json", "tigers")
    WOLVES = get_user_list("elevated_users.json", "whitelists")
    DONATION_LINK = None  # EG, paypal
    CERT_PATH = None
    PORT = 5000
    DEL_CMDS = True  # Delete commands that users dont have access to, like delete /ban if a non admin uses it.
    STRICT_GBAN = True
    WORKERS = (
        8  # Number of subthreads to use. Set as number of threads your processor uses
    )
    BAN_STICKER = ""  # banhammer marie sticker id, the bot will send this sticker before banning or kicking a user in chat.
    ALLOW_EXCL = True  # Allow ! commands as well as / (Leave this to true so that blacklist can work)
    ALLOW_CHATS = True
    CASH_API_KEY = (
        "awoo"  # Get your API key from https://www.alphavantage.co/support/#api-key
    )
    TIME_API_KEY = "awoo"  # Get your API key from https://timezonedb.com/api
    WALL_API = (
        "awoo"  # For wallpapers, get one from https://wall.alphacoders.com/api.php
    )
    AI_API_KEY = "awoo"  # For chatbot, get one from https://coffeehouse.intellivoid.net/dashboard
    BL_CHATS = []  # List of groups that you want blacklisted.
    SPAMMERS = None
    

class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
