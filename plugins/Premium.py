import random
from datetime import timedelta
from asyncio import sleep 
import pytz
import datetime, time
from info import *
from Script import script 
from utils import get_seconds, get_status, temp
from database.users_chats_db import db 
from pyrogram import Client, filters 
from database.aman import delete_all_referal_users, get_referal_users_count
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
import traceback

REACTION = ["🔥", "❤️", "😍", "⚡", "👍", "👎", "❤", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "❤‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌", "🏆", "🍾", "💋", "🖕", "😈", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝", "✍", "🤗", "🫡", "🎅", "🎄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂", "🤷", "🤷‍♀", "😡"]

@Client.on_message(filters.command("premium"))
async def give_premium_cmd_handler(client, message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.reply("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        return
    if len(message.command) == 3:
        user_id = int(message.command[1])  # Convert the user_id to integer
        user = await client.get_users(user_id)
        time = message.command[2]        
        seconds = await get_seconds(time)
        if seconds > 0:
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            user_data = {"id": user_id, "expiry_time": expiry_time} 
            await db.update_user(user_data)  # Use the update_user method to update or insert user data
            await message.reply_text(f"ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴛᴏ ᴛʜᴇ ᴜꜱᴇʀꜱ.\n👤 ᴜꜱᴇʀ ɴᴀᴍᴇ : {user.mention}\n⚡ ᴜꜱᴇʀ ɪᴅ : {user.id}\n⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : {time}")
            time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            current_time = time_zone.strftime("%d-%m-%Y\n⏱️ ᴊᴏɪɴɪɴɢ ᴛɪᴍᴇ : %I:%M:%S %p")            
            expiry = expiry_time   
            expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : %I:%M:%S %p")  
            await client.send_message(
                chat_id=user_id,
                text=f"ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ꜰᴏʀ {time} ᴇɴᴊᴏʏ 😀\n\n⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {current_time}\n\n⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}",                
            )
            #user = await client.get_users(user_id)
            await client.send_message(PREMIUM_LOGS, text=f"#Added_Premium\n\n👤 ᴜꜱᴇʀ : {user.mention}\n⚡ ᴜꜱᴇʀ ɪᴅ : {user.id}\n⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : {time}\n\n⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {current_time}\n\n⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}", disable_web_page_preview=True)
                
        else:
            await message.reply_text("Invalid time format. Please use '1day for days', '1hour for hours', or '1min for minutes', or '1month for months' or '1year for year'")
    else:
        await message.reply_text("Usage: /premium user_id time \n\nExample /premium 1252789 10day \n\n(e.g. for time units '1day for days', '1hour for hours', or '1min for minutes', or '1month for months' or '1year for year')")
	   
@Client.on_message(filters.command("remove_premium") & filters.user(ADMINS))
async def remove_premium(client, message):
    if len(message.command) == 2:
        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        if await db.remove_premium_access(user_id):
            await message.reply_text("<b>sᴜᴄᴄᴇssꜰᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ 💔</b>")
            await client.send_message(
                chat_id=user_id,
                text=f"<b>ʜᴇʏ {user.mention},\n\nʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ 😕</b>"
            )
        else:
            await message.reply_text("<b>👀 ᴜɴᴀʙʟᴇ ᴛᴏ ʀᴇᴍᴏᴠᴇ, ᴀʀᴇ ʏᴏᴜ sᴜʀᴇ ɪᴛ ᴡᴀs ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ ɪᴅ??</b>")
    else:
        await message.reply_text("Usage: <code>/remove_premium user_id</code>")


@Client.on_message(filters.command("myplan"))
async def myplan(client, message):
    await message.react(emoji=random.choice(REACTION), big=True)
    aa = await message.reply_text("check your plan")
    await aa.delete()
    user = message.from_user.mention 
    user_id = message.from_user.id
    data = await db.get_user(message.from_user.id)
    has_free_trial = await db.check_trial_status(user_id)
    if data and data.get("expiry_time"):
        expiry = data.get("expiry_time") 
        expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
        expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y  ⏰: %I:%M:%S %p")            
        current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        time_left = expiry_ist - current_time
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
        await message.reply_text(f"📝 <u>ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ ᴅᴇᴛᴀɪʟꜱ</u> :\n\n👤 ᴜꜱᴇʀ ɴᴀᴍᴇ : {user}\n🏷️ ᴜꜱᴇʀ ɪᴅ : <code>{user_id}</code>\n⏱️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : {time_left_str}")
#: {user}\n🪙 User Id: <code>{user_id}</code>\n⏰ Time Left: {time_left_str}\n⌛️ Expiry: {}.")   
    else:
        btn = [                                
            [InlineKeyboardButton('🤞🏻ɢᴇᴛ ʟᴏᴡ ᴘʀɪᴄᴇ ᴘʟᴀɴs 🍿', callback_data='seeplans')]]
    #if not has_free_trial:
	#btn.append([InlineKeyboardButton("🔰ɢᴇᴛ 5 ᴍɪɴᴜᴛᴇs ꜰʀᴇᴇ ᴛʀᴀɪʟ🔰", callback_data='give_trial')])            
        reply_markup = InlineKeyboardMarkup(btn)         
        await message.reply_text(f"**Hey {user}.. 💔\n\nYou Do Not Have Any Active Premium Plans, If You Want To Take Premium Then Click on /plan To Know About The Plan**",reply_markup=reply_markup)
        
@Client.on_message(filters.command("check_plan") & filters.user(ADMINS))
async def check_plan(client, message):
    if len(message.text.split()) == 1:
        await message.reply_text("use this command with user id... like\n\n /check_plan user_id")
        return
    user_id = int(message.text.split(' ')[1])
    user_data = await db.get_user(user_id)

    if user_data and user_data.get("expiry_time"):
        expiry = user_data.get("expiry_time")
        expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
        expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y %I:%M:%S %p")
        current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        time_left = expiry_ist - current_time
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
        response = (
            f"User ID: {user_id}\n"
            f"Name: {(await client.get_users(user_id)).mention}\n"
            f"Expiry Date: {expiry_str_in_ist}\n"
            f"Expiry Time: {time_left_str}"
        )
    else:
        response = "User have not a premium..."
    await message.reply_text(response)

@Client.on_message(filters.command('plan') & filters.incoming)
async def plan(client, message):
    await message.react(emoji=random.choice(REACTION), big=True)
    user_id = message.from_user.id
    if message.from_user.username:
        user_info = f"@{message.from_user.username}"
    else:
        user_info = f"{message.from_user.mention}"
    log_message = f"<b><u>🚫 ᴛʜɪs ᴜsᴇʀs ᴛʀʏ ᴛᴏ ᴄʜᴇᴄᴋ /plan</u> {temp.B_LINK}\n\n- ɪᴅ - `{user_id}`\n- ɴᴀᴍᴇ - {user_info}</b>"
    btn = [
        [InlineKeyboardButton('🤞🏻ɢᴇᴛ ʟᴏᴡ ᴘʀɪᴄᴇ ᴘʟᴀɴs 🍿', callback_data='premium_info')],
        [
        InlineKeyboardButton("🗑 ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ 🗑", callback_data="close_data")
    ]]
    await message.reply_photo(
        photo=(QR_CODE),
        caption=script.PREMIUM_TEXT.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(btn))
    await client.send_message(PREMIUM_LOGS, log_message)

@Client.on_message(filters.command("premium_user") & filters.user(ADMINS))
async def premium_user(client, message):
    aa = await message.reply_text("Fetching ...")  
    users = await db.get_all_users()
    users_list = []
    async for user in users:
        users_list.append(user)    
    user_data = {user['id']: await db.get_user(user['id']) for user in users_list}    
    new_users = []
    for user in users_list:
        user_id = user['id']
        data = user_data.get(user_id)
        expiry = data.get("expiry_time") if data else None        
        if expiry:
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            expiry_str_in_ist = expiry_ist.strftime("%d-%m-%Y %I:%M:%S %p")          
            current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            time_left = expiry_ist - current_time
            days, remainder = divmod(time_left.total_seconds(), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, _ = divmod(remainder, 60)            
            time_left_str = f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes"            
            user_info = await client.get_users(user_id)
            user_str = (
                f"{len(new_users) + 1}. User ID: {user_id}\n"
                f"Name: {user_info.mention}\n"
                f"Expiry Date: {expiry_str_in_ist}\n"
                f"Expiry Time: {time_left_str}\n\n"
            )
            new_users.append(user_str)
    new = "Paid Users - \n\n" + "\n".join(new_users)   
    try:
        await aa.edit_text(new)
    except MessageTooLong:
        with open('usersplan.txt', 'w+') as outfile:
            outfile.write(new)
        await message.reply_document('usersplan.txt', caption="Paid Users:")
        
@Client.on_message(filters.command('refer') & filters.incoming)
async def refer(client, message):
    await message.react(emoji=random.choice(REACTION), big=True)
    m = await message.reply_text(f"<b>Generating Your Refferal Link...</b>")
   # await m.delete()
   # await asyncio.sleep(1)
    await m.delete()
    actual_referral_count = await get_referal_users_count(message.from_user.id)
    user_id = message.from_user.id
    if message.from_user.username:
        user_info = f"@{message.from_user.username}"
    else:
        user_info = f"{message.from_user.mention}"
    log_message = f"<b><u>🚫 ᴛʜɪs ᴜsᴇʀs ᴛʀʏ ᴛᴏ ᴄʜᴇᴄᴋ /refer</u> {temp.B_LINK}\n\n- ɪᴅ - `{user_id}`\n- ɴᴀᴍᴇ - {user_info}</b>"
    btn = [[
	    InlineKeyboardButton('invite link', url=f'https://telegram.me/share/url?url=https://t.me/{temp.U_NAME}?start=reff_{message.from_user.id}&text=Hello%21%20Experience%20a%20bot%20that%20offers%20a%20vast%20library%20of%20unlimited%20movies%20and%20series.%20%F0%9F%98%83'),
        InlineKeyboardButton(f'⏳ {actual_referral_count}', callback_data='show_referral_count'),
        InlineKeyboardButton('Cʟᴏsᴇ', callback_data='close_data')
    ]]  
    await message.reply_photo(
        photo=(REFER_PICS),
        caption=script.REFER_TEXT.format(temp.U_NAME, message.from_user.id),
	reply_markup=InlineKeyboardMarkup(btn))
    await client.send_message(PREMIUM_LOGS, log_message)

async def add_premium(client, userid): 
    user_id = int(userid) 
    time = REFERAL_PREMEIUM_TIME
    seconds = await get_seconds(time)
    if seconds > 0:
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        user_data = {"id": user_id, "expiry_time": expiry_time} 
        await db.update_user(user_data)  # Use the update_user method to update or insert user data
        await delete_all_referal_users(user_id)
        await client.send_message(chat_id = user_id, text = "<b>You Have Successfully Completed Total Referal.\n\nYou Added In Premium For {}</b>".format(REFERAL_PREMEIUM_TIME))
   # else:
        await client.send_message(PREMIUM_LOGS, text=f"#reffer_Premium\n\nSᴜᴄᴄᴇss ғᴜʟʟʏ reffral ᴛᴀsᴋ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ʙʏ ᴛʜɪs ᴜsᴇʀ:\n\nuser Nᴀᴍᴇ: {message.from_user.mention} \n\nUsᴇʀ ɪ!")	

        
