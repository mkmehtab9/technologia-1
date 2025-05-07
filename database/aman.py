from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient
import datetime
import pytz
from motor.motor_asyncio import AsyncIOMotorClient
from info import *

my_client = MongoClient(DATABASE_URI)
mydb = my_client["referal_user"]

async def referal_add_user(user_id, ref_user_id):
    user_db = mydb[str(user_id)]
    user = {'_id': ref_user_id}
    try:
        user_db.insert_one(user)
        return True
    except DuplicateKeyError:
        return False
    

async def get_referal_all_users(user_id):
    user_db = mydb[str(user_id)]
    return user_db.find()
    
async def get_referal_users_count(user_id):
    user_db = mydb[str(user_id)]
    count = user_db.count_documents({})
    return count
    

async def delete_all_referal_users(user_id):
    user_db = mydb[str(user_id)]
    user_db.delete_many({}) 
