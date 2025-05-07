import datetime
import pytz
from motor.motor_asyncio import AsyncIOMotorClient
from info import *

client = AsyncIOMotorClient(DATABASE_URI)
mydb = client[DATABASE_NAME]
fsubs = client['fsubs']

class Database:
    default = {
        'spell_check': SPELL_CHECK,
        'auto_filter': AUTO_FILTER,
        'file_secure': PROTECT_CONTENT,
        'auto_delete': AUTO_DELETE,
        'template': IMDB_TEMPLATE,
        'caption': FILE_CAPTION,
        'tutorial': TUTORIAL,
        'tutorial_2': TUTORIAL_2,
        'shortner': SHORTENER_WEBSITE,
        'api': SHORTENER_API,
        'shortner_two': SHORTENER_WEBSITE2,
        'api_two': SHORTENER_API2,
        'log': LOG_VR_CHANNEL,
        'imdb': IMDB,
        'link': LINK_MODE,
        'is_verify': IS_VERIFY,
        'verify_time': TWO_VERIFY_GAP,
        'welcome': MELCOW_NEW_USERS
    }
    
    def __init__(self):
        self.col = mydb.users
        self.grp = mydb.groups
        self.misc = mydb.misc
        self.verify_id = mydb.verify_id
        self.users = mydb.uersz
        self.req = mydb.requests
        self.grp_and_ids = fsubs.grp_and_ids
        self.botcol = mydb.botcol
        self.ads_link = mydb.ads_link
        
    def new_user(self, id, name):
        return dict(
            id=id,
            name=name,
            point=0,
            ban_status=dict(is_banned=False, ban_reason="")
        )
    
    def new_group(self, id, title, owner_id):
        return dict(
            id=id,
            title=title,
            owner_id=owner_id,
            is_verified=False,
            is_rejected=False,
            chat_status=dict(is_disabled=False, reason=""),
            settings=self.default  # Initialize with default settings
        )
    
    async def add_chat(self, chat, title, owner_id):
        chat = self.new_group(chat, title, owner_id)
        await self.grp.insert_one(chat)
        print(f"Added new group {chat['id']} with default settings: {chat['settings']}")
    
    async def get_settings(self, id):
        chat = await self.grp.find_one({'id': int(id)})
        if chat and 'settings' in chat:
            print(f"Retrieved settings for group {id}: {chat['settings']}")
            return chat['settings']
        print(f"No settings found for group {id}, returning default: {self.default}")
        return self.default

    async def update_settings(self, id, settings):
        result = await self.grp.update_one(
            {'id': int(id)},
            {'$set': {'settings': settings}},
            upsert=True  # Create the document if it doesn’t exist
        )
        if result.matched_count > 0 or result.upserted_id:
            print(f"Successfully updated settings for group {id}: {settings}")
        else:
            print(f"Failed to update settings for group {id}")

    async def find_join_req(self, id):
        return bool(await self.req.find_one({'id': id}))
        
    async def add_join_req(self, id):
        await self.req.insert_one({'id': id})

    async def del_join_req(self):
        await self.req.drop()
        
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
        
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def delete_chat(self, id):
        await self.grp.delete_many({'id': int(id)})
        
    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats
    
    async def get_chat(self, chat_id):
        chat = await self.grp.find_one({'id': int(chat_id)})
        return chat if chat else False  

    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count
    
    async def get_all_chats(self):
        return self.grp.find({})

    async def get_db_size(self):
        return (await mydb.command("dbstats"))['dataSize'] 

    async def get_notcopy_user(self, user_id):
        user_id = int(user_id)
        user = await self.misc.find_one({"user_id": user_id})
        ist_timezone = pytz.timezone('Asia/Kolkata')
        if not user:
            res = {
                "user_id": user_id,
                "last_verified": datetime.datetime(2020, 5, 17, 0, 0, 0, tzinfo=ist_timezone),
                "second_time_verified": datetime.datetime(2019, 5, 17, 0, 0, 0, tzinfo=ist_timezone),
            }
            user = await self.misc.insert_one(res)
        return user

    async def update_notcopy_user(self, user_id, value: dict):
        user_id = int(user_id)
        myquery = {"user_id": user_id}
        newvalues = {"$set": value}
        return await self.misc.update_one(myquery, newvalues)

    async def is_user_verified(self, user_id):
        user = await self.get_notcopy_user(user_id)
        try:
            pastDate = user["last_verified"]
        except Exception:
            user = await self.get_notcopy_user(user_id)
            pastDate = user["last_verified"]
        ist_timezone = pytz.timezone('Asia/Kolkata')
        pastDate = pastDate.astimezone(ist_timezone)
        current_time = datetime.datetime.now(tz=ist_timezone)
        seconds_since_midnight = (current_time - datetime.datetime(current_time.year, current_time.month, current_time.day, 0, 0, 0, tzinfo=ist_timezone)).total_seconds()
        time_diff = current_time - pastDate
        total_seconds = time_diff.total_seconds()
        return total_seconds <= seconds_since_midnight

    async def user_verified(self, user_id):
        user = await self.get_notcopy_user(user_id)
        try:
            pastDate = user["second_time_verified"]
        except Exception:
            user = await self.get_notcopy_user(user_id)
            pastDate = user["second_time_verified"]
        ist_timezone = pytz.timezone('Asia/Kolkata')
        pastDate = pastDate.astimezone(ist_timezone)
        current_time = datetime.datetime.now(tz=ist_timezone)
        seconds_since_midnight = (current_time - datetime.datetime(current_time.year, current_time.month, current_time.day, 0, 0, 0, tzinfo=ist_timezone)).total_seconds()
        time_diff = current_time - pastDate
        total_seconds = time_diff.total_seconds()
        return total_seconds <= seconds_since_midnight

    async def use_second_shortener(self, user_id, time):
        user = await self.get_notcopy_user(user_id)
        if not user.get("second_time_verified"):
            ist_timezone = pytz.timezone('Asia/Kolkata')
            await self.update_notcopy_user(user_id, {"second_time_verified": datetime.datetime(2019, 5, 17, 0, 0, 0, tzinfo=ist_timezone)})
            user = await self.get_notcopy_user(user_id)
        if await self.is_user_verified(user_id):
            try:
                pastDate = user["last_verified"]
            except Exception:
                user = await self.get_notcopy_user(user_id)
                pastDate = user["last_verified"]
            ist_timezone = pytz.timezone('Asia/Kolkata')
            pastDate = pastDate.astimezone(ist_timezone)
            current_time = datetime.datetime.now(tz=ist_timezone)
            time_difference = current_time - pastDate
            if time_difference > datetime.timedelta(seconds=time):
                pastDate = user["last_verified"].astimezone(ist_timezone)
                second_time = user["second_time_verified"].astimezone(ist_timezone)
                return second_time < pastDate
        return False
   
    async def create_verify_id(self, user_id: int, hash):
        res = {"user_id": user_id, "hash": hash, "verified": False}
        return await self.verify_id.insert_one(res)

    async def get_verify_id_info(self, user_id: int, hash):
        return await self.verify_id.find_one({"user_id": user_id, "hash": hash})

    async def update_verify_id_info(self, user_id, hash, value: dict):
        myquery = {"user_id": user_id, "hash": hash}
        newvalues = {"$set": value}
        return await self.verify_id.update_one(myquery, newvalues)

    async def get_user(self, user_id):
        user_data = await self.users.find_one({"id": user_id})
        return user_data
        
    async def update_user(self, user_data):
        await self.users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)

    async def has_premium_access(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            expiry_time = user_data.get("expiry_time")
            if expiry_time is None:
                return False
            elif isinstance(expiry_time, datetime.datetime) and datetime.datetime.now() <= expiry_time:
                return True
            else:
                await self.users.update_one({"id": user_id}, {"$set": {"expiry_time": None}})
        return False
        
    async def update_one(self, filter_query, update_data):
        try:
            result = await self.users.update_one(filter_query, update_data)
            return result.matched_count == 1
        except Exception as e:
            print(f"Error updating document: {e}")
            return False
            
    async def all_premium_users_count(self):
        count = await self.users.count_documents({
            "expiry_time": {"$gt": datetime.datetime.now()}
        })
        return count
        
    async def get_expired(self, current_time):
        expired_users = []
        if data := self.users.find({"expiry_time": {"$lt": current_time}}):
            async for user in data:
                expired_users.append(user)
        return expired_users

    async def remove_premium_access(self, user_id):
        return await self.update_one(
            {"id": user_id}, {"$set": {"expiry_time": None}}
        )

    async def setFsub(self, grpID, fsubID):
        return await self.grp_and_ids.update_one({'grpID': grpID}, {'$set': {'grpID': grpID, "fsubID": fsubID}}, upsert=True)   
        
    async def getFsub(self, grpID):
        link = await self.grp_and_ids.find_one({"grpID": grpID})
        if link is not None:
            return link.get("fsubID")
        else:
            return None
            
    async def delFsub(self, grpID):
        result = await self.grp_and_ids.delete_one({"grpID": grpID})
        if result.deleted_count != 0:
            return True
        else:
            return False

    async def get_send_movie_update_status(self, bot_id):
        bot = await self.botcol.find_one({'id': bot_id})
        if bot and bot.get('movie_update_feature'):
            return bot['movie_update_feature']
        else:
            return IS_SEND_MOVIE_UPDATE

    async def update_send_movie_update_status(self, bot_id, enable):
        bot = await self.botcol.find_one({'id': int(bot_id)})
        if bot:
            await self.botcol.update_one({'id': int(bot_id)}, {'$set': {'movie_update_feature': enable}})
        else:
            await self.botcol.insert_one({'id': int(bot_id), 'movie_update_feature': enable})            
            
    async def get_pm_search_status(self, bot_id):
        bot = await self.botcol.find_one({'id': bot_id})
        if bot and bot.get('bot_pm_search'):
            return bot['bot_pm_search']
        else:
            return IS_PM_SEARCH

    async def update_pm_search_status(self, bot_id, enable):
        bot = await self.botcol.find_one({'id': int(bot_id)})
        if bot:
            await self.botcol.update_one({'id': int(bot_id)}, {'$set': {'bot_pm_search': enable}})
        else:
            await self.botcol.insert_one({'id': int(bot_id), 'bot_pm_search': enable})
            
    async def verify_group(self, chat_id):
        await self.grp.update_one({'id': int(chat_id)}, {'$set': {'is_verified': True}})

    async def un_rejected(self, chat_id):
        await self.grp.update_one({'id': int(chat_id)}, {'$set': {'is_rejected': False}})
        
    async def reject_group(self, chat_id):
        await self.grp.update_one({'id': int(chat_id)}, {'$set': {'is_rejected': True}})
        
    async def check_group_verification(self, chat_id):
        chat = await self.get_chat(chat_id)
        if not chat:
            return False
        return chat.get('is_verified')
        
    async def rejected_group(self, chat_id):
        chat = await self.get_chat(chat_id)
        if not chat:
            return False
        return chat.get('is_rejected')
        
    async def get_all_groups(self):
        return await self.grp.find().to_list(None)
        
    async def delete_all_groups(self):
        await self.grp.delete_many({})

    async def check_trial_status(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            return user_data.get("has_free_trial", False)
        return False

    async def give_free_trial(self, user_id):
        user_id = user_id
        seconds = 5 * 60         
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        user_data = {"id": user_id, "expiry_time": expiry_time, "has_free_trial": True}
        await self.users.update_one({"id": user_id}, {"$set": user_data}, upsert=True)

    async def reset_free_trial(self, user_id=None):
        if user_id is None:
            update_data = {"$set": {"has_free_trial": False}}
            result = await self.users.update_many({}, update_data)
            return result.modified_count
        else:
            update_data = {"$set": {"has_free_trial": False}}
            result = await self.users.update_one({"id": user_id}, update_data)
            return 1 if result.modified_count > 0 else 0

    async def set_ads_link(self, link):
        await self.ads_link.update_one({}, {'$set': {'link': link}}, upsert=True)
        
    async def get_ads_link(self):
        link = await self.ads_link.find_one({})
        if link is not None:
            return link.get("link")
        else:
            return None
            
    async def del_ads_link(self):
        try: 
            isDeleted = await self.ads_link.delete_one({})
            if isDeleted.deleted_count > 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"Got err in db set: {e}")
            return False
            
db = Database()
