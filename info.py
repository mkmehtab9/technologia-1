import re
import os
from os import environ
from Script import script
from collections import defaultdict
from pyrogram import Client

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Main variables
API_ID = int(environ.get('API_ID', '22470161'))
API_HASH = environ.get('API_HASH', '1360539223d4b5c2eecad27f9cac40c5')
BOT_TOKEN = environ.get('BOT_TOKEN', '7733173048:AAH1_jZLbZqqMzAHZiqQ110JXPe9WoSnqIY')

ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '1586261625').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1001952883830').split()]
MOVIE_UPDATE = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('MOVIE_UPDATE', '-1002122516919').split()]
DELETE_CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('DELETE_CHANNELS', '-1002122516919').split()]  # Fixed dch to ch
AUTH_CHANNEL = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('AUTH_CHANNEL', '-1002251903769').split()]

USERNAME = environ.get('USERNAME', "https://t.me/@Arya_2530")
MOVIE_GROUP_LINK = environ.get('MOVIE_GROUP_LINK', 'https://t.me/+Or0VDrXEy8AyYzA1')
GRP_LNK = environ.get('GRP_LNK', 'https://t.me/')
TUTORIAL = environ.get("TUTORIAL", "t.me//42")
TUTORIAL_2 = environ.get("TUTORIAL_2", "https://t.me//42")
STREAMHTO = (environ.get('STREAMHTO', 'https://t.me/'))
URL = environ.get('URL', 'http://...22:8000')

LOG_VR_CHANNEL = int(environ.get('LOG_VR_CHANNEL', '-1002298769311'))
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1002689335197'))
LOG_API_CHANNEL = int(environ.get('LOG_API_CHANNEL', '-1002689335197'))
MOVIE_UPDATE_CHANNEL = int(environ.get('MOVIE_UPDATE_CHANNEL', '-1002689335197'))
PREMIUM_LOGS = int(environ.get('PREMIUM_LOGS', '-1002552714461'))
SUPPORT_GROUP = int(environ.get('SUPPORT_GROUP', '-1002251903769'))  # Replace with correct ID
REQ_CHANNEL = int(environ.get('REQ_CHANNEL', '-1002689335197')) 
BIN_CHANNEL = int(environ.get('BIN_CHANNEL', '-1002571082220'))

DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://yashdd:yoman@yashdd.2rsdjsv.mongodb.net/?retryWrites=true&w=majority&appName=yashdd")
DATABASE_URI2 = environ.get('DATABASE_URI2', "mongodb+srv://yashdd:yoman@yashdd.2rsdjsv.mongodb.net/?retryWrites=true&w=majority&appName=yashdd")
DATABASE_NAME = environ.get('DATABASE_NAME', "yashdd")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'movies')

WELCOME_VID = environ.get("WELCOME_VID", "https://telegra.ph/file/451f038b4e7c2ddd10dc0.mp4")
QR_CODE = environ.get('QR_CODE', 'https://i.ibb.co/4ZBGF89w/photo-2024-04-13-10-32-08-7477941501499015184.jpg')
QR = environ.get('QR', 'https://i.ibb.co/4ZBGF89w/photo-2024-04-13-10-32-08-7477941501499015184.jpg')
REFER_PICS = environ.get("REFER_PICS", "https://graph.org/file/1a2e64aee3d4d10edd930.jpg")
START_IMG = environ.get('START_IMG', 'https://envs.sh/bNy.jpg').split()
MONEY_IMG = environ.get('MONEY_IMG', 'https://graph.org/file/f53094fbcccead10fb6e7.jpg')
VERIFY_IMG = environ.get("VERIFY_IMG", "https://graph.org/file/1669ab9af68eaa62c3ca4.jpg")

REFERAL_COUNT = int(environ.get('REFERAL_COUNT', '15'))
REFERAL_PREMEIUM_TIME = environ.get('REFERAL_PREMEIUM_TIME', '7day')

STREAM_API = (environ.get('STREAM_API', 'b53e4769ab3cc30124a32cb9c27496c7ddaddecc'))
SHORTENER_API = environ.get("SHORTENER_API", "1ec5154e19e7e771b5987cf0952261f0b489125d")
SHORTENER_API2 = environ.get("SHORTENER_API2", "30fb79c81157036d36e76dca142ebfba6291c4a0")
SHORTENER_WEBSITE = environ.get("SHORTENER_WEBSITE", 'Arlinks.in')
SHORTENER_WEBSITE2 = environ.get("SHORTENER_WEBSITE2", 'Arlinks.in')
STREAM_SITE = (environ.get('STREAM_SITE', 'gplinks.com'))

LANGUAGES = ["hindi", "english", "telugu", "tamil", "kannada", "malayalam", "bengali", "marathi", "gujarati", "punjabi"]
QUALITIES = ["480p", "720p", "1080p", "HdRip", "1440p", "2160p"]
SEASONS = [f'season {i}' for i in range(1, 23)]

FILE_AUTO_DEL_TIMER = int(environ.get('FILE_AUTO_DEL_TIMER', '600'))
DELETE_TIME = int(environ.get('DELETE_TIME', 300))
TWO_VERIFY_GAP = int(environ.get('TWO_VERIFY_GAP', "43200"))

FILE_CAPTION = environ.get('FILE_CAPTION', f'{script.FILE_CAPTION}')
IMDB_TEMPLATE = environ.get('IMDB_TEMPLATE', f'{script.IMDB_TEMPLATE_TXT}')

PORT = os.environ.get('PORT', '8004')
MAX_BTN = int(environ.get('MAX_BTN', '8'))

MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "False")), False)
NO_RESULTS_MSG = is_enabled((environ.get("NO_RESULTS_MSG", 'True')), False)
IS_SEND_MOVIE_UPDATE = is_enabled('IS_SEND_MOVIE_UPDATE', False) 
IS_PM_SEARCH = is_enabled('IS_PM_SEARCH', False) 
AUTO_FILTER = is_enabled('AUTO_FILTER', True)
IS_VERIFY = is_enabled('IS_VERIFY', True)
AUTO_DELETE = is_enabled('AUTO_DELETE', True)
IMDB = is_enabled('IMDB', False)
LONG_IMDB_DESCRIPTION = is_enabled('LONG_IMDB_DESCRIPTION', False)
PROTECT_CONTENT = is_enabled('PROTECT_CONTENT', False)
SPELL_CHECK = is_enabled('SPELL_CHECK', True)
LINK_MODE = is_enabled('LINK_MODE', True)
