
import os, requests
import logging
import random
import asyncio
import string
import pytz
from datetime import timedelta
from datetime import datetime as dt
from Script import script
from pyrogram import Client, filters, enums
from database.ia_filterdb import Media, get_file_details, get_bad_files, unpack_new_file_id
from database.users_chats_db import db
from database.config_db import mdb
from info import *
from plugins.Premium import add_premium
from plugins.pm_filter import auto_filter
from database.aman import referal_add_user, get_referal_all_users, get_referal_users_count, delete_all_referal_users
from utils import get_settings,get_seconds, save_group_settings, is_subscribed, get_size, get_shortlink, is_check_admin, get_status, temp, get_readable_time
import re
import base64
from pyrogram.types import *
from pyrogram.errors import *
import traceback

logger = logging.getLogger(__name__)
REACTION = ["🔥", "❤️", "😍", "⚡", "👍", "👎", "❤", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "❤‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌", "🏆", "🍾", "💋", "🖕", "😈", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝", "✍", "🤗", "🫡", "🎅", "🎄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂", "🤷", "🤷‍♀", "😡"]

# CHECK COMPONENTS FOLDER FOR MORE COMMANDS
@Client.on_message(filters.command("invite") & filters.private & filters.user(ADMINS))
async def invite(client, message):
    toGenInvLink = message.command[1]
    if len(toGenInvLink) != 14:
        return await message.reply("Invalid chat id\nAdd -100 before chat id if You did not add any yet.") 
    try:
        link = await client.export_chat_invite_link(toGenInvLink)
        await message.reply(link)
    except Exception as e:
        print(f'Error while generating invite link : {e}\nFor chat:{toGenInvLink}')
        await message.reply(f'Error while generating invite link : {e}\nFor chat:{toGenInvLink}')
   
@Client.on_message(filters.command("start") & filters.incoming)
async def start(client: Client, message):
    await message.react(emoji=random.choice(REACTION), big=True)
    m = message
    user_id = m.from_user.id
    
    # Handle notcopy verification
    if len(m.command) == 2 and m.command[1].startswith('notcopy'):
        _, userid, verify_id, file_id = m.command[1].split("_", 3)
        user_id = int(userid)
        grp_id = temp.CHAT.get(user_id, 0)
        settings = await get_settings(grp_id)
        verify_id_info = await db.get_verify_id_info(user_id, verify_id)
        if not verify_id_info or verify_id_info["verified"]:
            await message.reply("<b>ʟɪɴᴋ ᴇxᴘɪʀᴇᴅ ᴛʀʏ ᴀɢᴀɪɴ...</b>")
            return
        ist_timezone = pytz.timezone('Asia/Kolkata')
        key = "second_time_verified" if await db.is_user_verified(user_id) else "last_verified"
        current_time = dt.now(tz=ist_timezone)
        result = await db.update_notcopy_user(user_id, {key: current_time})
        await db.update_verify_id_info(user_id, verify_id, {"verified": True})
        num = 2 if key == "second_time_verified" else 1
        msg = script.SECOND_VERIFY_COMPLETE_TEXT if key == "second_time_verified" else script.VERIFY_COMPLETE_TEXT
        await client.send_message(settings['log'], script.VERIFIED_LOG_TEXT.format(m.from_user.mention, user_id, dt.now(pytz.timezone('Asia/Kolkata')).strftime('%d %B %Y'), num))
        btn = [[
            InlineKeyboardButton("‼ ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ꜰɪʟᴇ ‼", url=f"https://telegram.me/{temp.U_NAME}?start=file_{grp_id}_{file_id}"),
        ]]
        reply_markup = InlineKeyboardMarkup(btn)
        await m.reply_photo(
            photo=(VERIFY_IMG),
            caption=msg.format(message.from_user.mention, get_readable_time(TWO_VERIFY_GAP)),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return

    # Handle getfile command
    if len(message.command) == 2 and message.command[1].startswith('getfile'):
        searches = message.command[1].split("-", 1)[1]
        search = searches.replace('-', ' ')
        message.text = search
        await auto_filter(client, message)
        return

    # Handle ads command
    if len(message.command) == 2 and message.command[1] in ["ads"]:
        msg, _, impression = await mdb.get_advirtisment()
        user = await db.get_user(message.from_user.id)
        seen_ads = user.get("seen_ads", False)
        ADS_LINK = await db.get_ads_link()
        buttons = [[
            InlineKeyboardButton('❌ ᴄʟᴏꜱᴇ ❌', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        if msg:
            await message.reply_photo(
                photo=ADS_LINK if ADS_LINK else URL,
                caption=msg,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            if impression is not None and not seen_ads:
                await mdb.update_advirtisment_impression(int(impression) - 1)
                await db.update_value(message.from_user.id, "seen_ads", True)
        else:
            await message.reply("<b>No Ads Found</b>")
        await mdb.reset_advertisement_if_expired()
        if msg is None and seen_ads:
            await db.update_value(message.from_user.id, "seen_ads", False)
        return

    # Handle group start
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [[
            InlineKeyboardButton('❤ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ❤', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ], [
            InlineKeyboardButton('𝗗𝗥𝗔𝗚𝗢𝗡 𝗕𝗢𝗧𝗭 🤖', url='https://t.me/moviehiap')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.GSTART_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup, disable_web_page_preview=True)
        if (str(message.chat.id)).startswith("-100") and not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            group_link = await message.chat.export_invite_link()
            user = message.from_user.mention if message.from_user else "Dear"
            await client.send_message(LOG_CHANNEL, script.NEW_GROUP_TXT.format(temp.B_LINK, message.chat.title, message.chat.id, message.chat.username, group_link, total, user))
            await db.add_chat(message.chat.id, message.chat.title, message.from_user.id)
        return

    # Add new user to database
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.NEW_USER_TXT.format(temp.B_LINK, message.from_user.id, message.from_user.mention))

    # Default start message in PM
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs ⇆', url=f'http://t.me/{temp.U_NAME}?startgroup=start')
        ], [
            InlineKeyboardButton('🔖 ᴄᴏᴍᴍᴀɴᴅs ', callback_data='commands'),
            InlineKeyboardButton('🎁 ᴘᴀɪᴅ ᴘʀᴏᴍᴏᴛɪᴏɴ ', callback_data="avads")
        ], [
            InlineKeyboardButton('ꜰʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ ✨', callback_data="subscription"),
            InlineKeyboardButton('✘ ᴀʙᴏᴜᴛ ', callback_data='about')
        ], [
            InlineKeyboardButton('☢ ᴇᴀʀɴɴ ᴍᴏɴᴇʏ ᴡɪᴛʜ ʙᴏᴛ ☢', callback_data='earn')
        ], [
            InlineKeyboardButton('💸 ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ : ʀᴇᴍᴏᴠᴇ ᴀᴅꜽ 💸', callback_data="premium_info"),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(START_IMG),
            caption=script.START_TXT.format(message.from_user.mention, get_status(), message.from_user.id),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return

    # PM Fsub check using group-specific fsub
    data = message.command[1]
    logger.info(f"Processing /start with data: {data}")
    try:
        pre, grp_id, file_id = data.split('_', 2)
        logger.info(f"Parsed data - pre: {pre}, grp_id: {grp_id}, file_id: {file_id}")
    except ValueError:
        logger.warning(f"Invalid data format: {data}. Falling back to default.")
        pre, grp_id, file_id = "", 0, data
    grp_id = int(grp_id) if grp_id else 0
    settings = await get_settings(grp_id) if grp_id else {}
    fsub_channel = settings.get('fsub', AUTH_CHANNEL)
    logger.info(f"Using fsub_channel: {fsub_channel} for group {grp_id}")
    if fsub_channel:
        try:
            await client.get_chat_member(fsub_channel, user_id)
            logger.info(f"User {user_id} is subscribed to {fsub_channel}. Proceeding to verification.")
        except UserNotParticipant:
            logger.info(f"User {user_id} not subscribed to {fsub_channel}. Showing fsub prompt.")
            invite_link = await client.export_chat_invite_link(fsub_channel)
            kk, file_id = message.command[1].split("_", 1)
            btn = [
                [InlineKeyboardButton("Join Channel", url=invite_link)],
                [InlineKeyboardButton("♻ ᴛʀʏ ᴀɢᴀɪɴ ♻", callback_data=f"checksub#{kk}#{file_id}")]
            ]
            await message.reply_text(
                text=f"<b>👋 Hello {message.from_user.mention},\n\nYᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴏғғɪᴄɪᴀʟ ᴏʀ ᴜᴭᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ғɪʀsᴛ. Tʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ '♻Try Again' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ.\n\nपहले आप हमारे चैनल को ज्वाइन करे फिर वापस आकर '♻Try Again' पर क्लिक करें आपको फाइल मिल जायेगी.</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            return
        except Exception as e:
            logger.error(f"Error checking fsub for channel {fsub_channel}: {e}")
            print(e)

    # If subscribed, proceed to verification or file handling
    user_id = m.from_user.id
    if not await db.has_premium_access(user_id):
        grp_id = int(grp_id)
        user_verified = await db.is_user_verified(user_id)
        settings = await get_settings(grp_id)
        is_second_shortener = await db.use_second_shortener(user_id, settings.get('verify_time', TWO_VERIFY_GAP))
        if (not user_verified or is_second_shortener) and settings.get("is_verify", IS_VERIFY):
            verify_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
            await db.create_verify_id(user_id, verify_id)
            temp.CHAT[user_id] = grp_id
            tutorial = settings.get('tutorial_2', TUTORIAL_2) if is_second_shortener else settings['tutorial']
            verify = await get_shortlink(f"https://telegram.me/{temp.U_NAME}?start=notcopy_{user_id}_{verify_id}_{file_id}", grp_id, is_second_shortener)
            buttons = [[
                InlineKeyboardButton("⚠ ᴠᴇʀɪꜰʏ ʟɪɴᴋ", url=verify),
                InlineKeyboardButton("⁉ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪꜰʏ", url=tutorial)
            ], [
                InlineKeyboardButton("🛍 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ (ɴᴏ ᴠᴇʀɪꜰʏ)", callback_data='seeplans')
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await m.reply_text(
                text=f"<b>👋 ʜᴇʏ {message.from_user.mention} ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 🌘,\n\n📌 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪꜰɪᴇᴅ ᴛᴏᴅᴀʏ 😐\nᴛᴀᴘ ᴏɴ ᴛʜᴇ ᴠᴇʀɪꜰʏ ʟɪɴᴋ & ɢᴇᴛ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss ꜰᴏʀ ᴛɪʟʟ ɴᴇxᴛ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ 😊.\n\n#ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ:- {'2/2' if is_second_shortener else '1/2'}\n\nɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴅɪʀᴇᴄᴛ ꜰɪʟᴇs ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ᴛᴀᴋᴇ ᴘʀᴇᴍɪᴜᴍ sᴇʀᴠɪᴄᴇ (ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪꜰʏ)</b>",
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return

    # Handle allfiles request
    if data and data.startswith("allfiles"):
        _, key = data.split("_", 1)
        files = temp.FILES_ID.get(key)
        if not files:
            await message.reply_text("<b>⚠ ᴀʟʟ ꜰɪʟᴇs ɴᴏᴛ ꜰᴏᴜɴᴅ ⚠</b>")
            return
        files_to_delete = []
        for file in files:
            user_id = message.from_user.id
            grp_id = temp.CHAT.get(user_id)
            settings = await get_settings(int(grp_id))
            CAPTION = settings['caption']
            f_caption = CAPTION.format(
                file_name=file.file_name,
                file_size=get_size(file.file_size),
                file_caption=file.caption
            )
            btn = [[
                InlineKeyboardButton("✛ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ ✛", callback_data=f'stream#{file.file_id}')
            ]]
            toDel = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file.file_id,
                caption=f_caption,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            files_to_delete.append(toDel)
        delCap = "<b>ᴀʟʟ {} ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ {} ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ᴠɪᴏʟᴀᴛɪᴏɴs!</b>".format(len(files_to_delete), f'{FILE_AUTO_DEL_TIMER / 60} ᴍɪɴᴜᴛᴇs' if FILE_AUTO_DEL_TIMER >= 60 else f'{FILE_AUTO_DEL_TIMER} sᴇᴄᴏɴᴅs')
        afterDelCap = "<b>ᴀʟʟ {} ғɪʟᴇs ᴀʀᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ {} ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ᴠɪᴏʟᴀᴛɪᴏɴs!</b>".format(len(files_to_delete), f'{FILE_AUTO_DEL_TIMER / 60} ᴍɪɴᴜᴛᴇs' if FILE_AUTO_DEL_TIMER >= 60 else f'{FILE_AUTO_DEL_TIMER} sᴇᴄᴏɴᴅs')
        replyed = await message.reply(delCap)
        await asyncio.sleep(FILE_AUTO_DEL_TIMER)
        for file in files_to_delete:
            try:
                await file.delete()
            except:
                pass
        return await replyed.edit(afterDelCap)

    if not data:
        return

    # Handle single file request
    files_ = await get_file_details(file_id)
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        return await message.reply('<b>⚠ ᴀʟʟ ꜰɪʟᴇs ɴᴏᴛ ꜰᴏᴜɴᴅ ⚠</b>')
    files = files_[0]
    settings = await get_settings(int(grp_id))
    CAPTION = settings['caption']
    f_caption = CAPTION.format(
        file_name=files.file_name,
        file_size=get_size(files.file_size),
        file_caption=files.caption
    )
    btn = [[
        InlineKeyboardButton("✛ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ ✛", callback_data=f'stream#{file_id}')
    ]]
    a = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=settings['file_secure'],
        reply_markup=InlineKeyboardMarkup(btn)
    )
    kkk = await a.reply_text("<b>⚠ᴛʜɪs ғɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ 10 ᴍɪɴᴜᴛᴇs🗑\n\nPʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ғɪʟᴇ ʙᴇғᴏʀᴇ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ🌴..</b>")
    await asyncio.sleep(FILE_AUTO_DEL_TIMER)
    await a.delete()
    await kkk.reply_text("<b>⚠ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛᴇᴅ ᴍᴏᴠɪᴇ ꜰɪʟᴇ ɪs ᴅᴇʟᴇᴛᴇᴅ, ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪɴ ʙᴏᴛ, ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴀɢᴀɪɴ ᴛʜᴇɴ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ ☺</b>")

@Client.on_callback_query(filters.regex(r'^checksub#'))
async def checksub_callback(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data  # e.g., "checksub#file#-1001234567890#12345"
    logger.info(f"Processing callback with data: {data}")
    
    # Split callback data
    parts = data.split('#')
    if len(parts) != 3:
        logger.error(f"Invalid callback format: {data}")
        # Fallback to AUTH_CHANNEL prompt if format is wrong
        invite_link = await client.export_chat_invite_link(AUTH_CHANNEL)
        btn = [
            [InlineKeyboardButton("Join Channel", url=invite_link)],
            [InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ ♻️", callback_data=data)]
        ]
        await callback_query.message.edit(
            text=f"<b>👋 Hello {callback_query.from_user.mention},\n\nYᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴏғғɪᴄɪᴀʟ ᴏʀ ᴜᴭᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ғɪʀsᴛ. Tʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ '♻️Try Again' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ.\n\nपहले आप हमारे चैनल को ज्वाइन करे फिर वापस आकर '♻️Try Again' पर क्लिक करें आपको फाइल मिल जायेगी.</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        await callback_query.answer("Join all channel", show_alert=True)
        return
    
    _, kk, file_id = parts  # kk = "file_-1001234567890", file_id = "12345"
    full_command = f"{kk}_{file_id}"  # e.g., "file_-1001234567890_12345"
    
    # Parse group ID more robustly
    try:
        command_parts = full_command.split('_')
        pre = command_parts[0]  # "file"
        grp_id = int(command_parts[1])  # "-1001234567890"
        file_id = '_'.join(command_parts[2:])  # "12345" or more if file_id has underscores
        logger.info(f"Parsed callback - pre: {pre}, grp_id: {grp_id}, file_id: {file_id}")
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing callback data {full_command}: {e}")
        # Fallback to AUTH_CHANNEL prompt if parsing fails
        invite_link = await client.export_chat_invite_link(AUTH_CHANNEL)
        btn = [
            [InlineKeyboardButton("Join Channel", url=invite_link)],
            [InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ ♻️", callback_data=data)]
        ]
        await callback_query.message.edit(
            text=f"<b>👋 Hello {callback_query.from_user.mention},\n\nYᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴏғғɪᴄɪᴀʟ ᴏʀ ᴜᴭᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ғɪʀsᴛ. Tʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ '♻️Try Again' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ.\n\nपहले आप हमारे चैनल को ज्वाइन करे फिर वापस आकर '♻️Try Again' पर क्लिक करें आपको फाइल मिल जायेगी.</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        await callback_query.answer("Join all channel", show_alert=True)
        return

    settings = await get_settings(grp_id)
    fsub_channel = settings.get('fsub', AUTH_CHANNEL)
    logger.info(f"Callback checksub - Using fsub_channel: {fsub_channel} for group {grp_id}")

    try:
        # Check subscription
        await client.get_chat_member(fsub_channel, user_id)
        logger.info(f"User {user_id} is subscribed to {fsub_channel}. Checking verification.")
    except UserNotParticipant:
        logger.info(f"User {user_id} still not subscribed to {fsub_channel}. Showing fsub prompt again.")
        invite_link = await client.export_chat_invite_link(fsub_channel)
        btn = [
            [InlineKeyboardButton("Join Channel", url=invite_link)],
            [InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ ♻️", callback_data=data)]  # Reuse original callback data
        ]
        await callback_query.message.edit(
            text=f"<b>👋 Hello {callback_query.from_user.mention},\n\nYᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴏғғɪᴄɪᴀʟ ᴏʀ ᴜᴭᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ғɪʀsᴛ. Tʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ '♻️Try Again' ʙᴜᴛᴛᴏɮ ʙᴇʟᴏᴡ.\n\nपहले आप हमारे चैनल को ज्वाइन करे फिर वापस आकर '♻️Try Again' पर क्लिक करें आपको फाइल मिल जायेगी.</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        await callback_query.answer("Join all channel", show_alert=True)  # Popup message added here
        return

    # If subscribed, check verification
    if not await db.has_premium_access(user_id):
        user_verified = await db.is_user_verified(user_id)
        is_second_shortener = await db.use_second_shortener(user_id, settings.get('verify_time', TWO_VERIFY_GAP))
        if (not user_verified or is_second_shortener) and settings.get("is_verify", IS_VERIFY):
            verify_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
            await db.create_verify_id(user_id, verify_id)
            temp.CHAT[user_id] = grp_id
            tutorial = settings.get('tutorial_2', TUTORIAL_2) if is_second_shortener else settings['tutorial']
            verify = await get_shortlink(f"https://telegram.me/{temp.U_NAME}?start=notcopy_{user_id}_{verify_id}_{file_id}", grp_id, is_second_shortener)
            buttons = [[
                InlineKeyboardButton("⚠️ ᴠᴇʀɪꜰʏ ʟɪɴᴋ", url=verify),
                InlineKeyboardButton("⁉️ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪꜰʏ", url=tutorial)
            ], [
                InlineKeyboardButton("🛍️ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ (ɴᴏ ᴠᴇʀɪꜰʏ)", callback_data='seeplans')
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await callback_query.message.edit(
                text=f"<b>👋 ʜᴇʏ {callback_query.from_user.mention} ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 🌘,\n\n📌 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪꜰɪᴇᴅ ᴛᴏᴅᴀʏ 😐\nᴛᴀᴘ ᴏɴ ᴛʜᴇ ᴠᴇʀɪꜰʏ ʟɪɴᴋ & ɢᴇᴛ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss ꜰᴏʀ ᴛɪʟʟ ɴᴇxᴛ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ 😊.\n\n#ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ:- {'2/2' if is_second_shortener else '1/2'}\n\nɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴅɪʀᴇᴄᴛ ꜰɪʟᴇs ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ᴛᴀᴋᴇ ᴘʀᴇᴍɪᴜᴍ sᴇʀᴠɪᴄᴇ (ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪꜰʏ)</b>",
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            await callback_query.answer()
            return

    # If verified or premium, deliver the file
    files_ = await get_file_details(file_id)
    if not files_:
        await callback_query.message.edit("<b>⚠️ ᴀʟʟ ꜰɪʟᴇs ɴᴏᴛ ꜰᴏᴜɴᴅ ⚠️</b>")
        return
    files = files_[0]
    CAPTION = settings['caption']
    f_caption = CAPTION.format(
        file_name=files.file_name,
        file_size=get_size(files.file_size),
        file_caption=files.caption
    )
    btn = [[
        InlineKeyboardButton("✛ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ ✛", callback_data=f'stream#{file_id}')
    ]]
    await callback_query.message.edit(
        text=f_caption,
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )
    await callback_query.answer()
	
@Client.on_message(filters.command('delete'))
async def delete(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('ᴏɴʟʏ ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ... 😑')
        return
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("ᴘʀᴏᴄᴇssɪɴɢ...⏳", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return
    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('<b>ᴛʜɪs ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ꜰɪʟᴇ ꜰᴏʀᴍᴀᴛ</b>')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)
    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('<b>ꜰɪʟᴇ ɪs sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ꜰʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ 💥</b>')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('<b>ꜰɪʟᴇ ɪs sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ꜰʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ 💥</b>')
        else:
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('<b>ꜰɪʟᴇ ɪs sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ꜰʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ 💥</b>')
            else:
                await msg.edit('<b>ꜰɪʟᴇ ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ</b>')

@Client.on_message(filters.command('deleteall'))
async def delete_all_index(bot, message):
    files = await Media.count_documents()
    if int(files) == 0:
        return await message.reply_text('Not have files to delete')
    btn = [[
            InlineKeyboardButton(text="ʏᴇs", callback_data="all_files_delete")
        ],[
            InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data="close_data")
        ]]
    if message.from_user.id not in ADMINS:
        await message.reply('ᴏɴʟʏ ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ... 😑')
        return
    await message.reply_text('<b>ᴛʜɪs ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ɪɴᴅᴇxᴇᴅ ꜰɪʟᴇs.\nᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ??</b>', reply_markup=InlineKeyboardMarkup(btn))

@Client.on_message(filters.command('settings'))
async def settings(client, message):
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return await message.reply("<b>💔 ʏᴏᴜ ᴀʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ...</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<code>ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘ.</code>")
    grp_id = message.chat.id
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ</b>')
    settings = await get_settings(grp_id)
    title = message.chat.title
    if settings is not None:
        buttons = [[
                InlineKeyboardButton('ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✓' if settings["auto_filter"] else 'ᴏғғ ✗', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}')
            ],[
                InlineKeyboardButton('ɪᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✓' if settings["imdb"] else 'ᴏғғ ✗', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}')
            ],[
                InlineKeyboardButton('sᴘᴇʟʟ ᴄʜᴇᴄᴋ', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✓' if settings["spell_check"] else 'ᴏғғ ✗', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}')
            ],[
                InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}'),
                InlineKeyboardButton(f'{get_readable_time(DELETE_TIME)}' if settings["auto_delete"] else 'ᴏғғ ✗', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}')
            ],[
                InlineKeyboardButton('ʀᴇsᴜʟᴛ ᴍᴏᴅᴇ', callback_data=f'setgs#link#{settings["link"]}#{str(grp_id)}'),
                InlineKeyboardButton('⛓ ʟɪɴᴋ' if settings["link"] else '🧲 ʙᴜᴛᴛᴏɴ', callback_data=f'setgs#link#{settings["link"]}#{str(grp_id)}')
            ],[
	        InlineKeyboardButton('ꜰɪʟᴇꜱ ᴍᴏᴅᴇ', callback_data=f'setgs#is_verify#{settings.get("is_verify", IS_VERIFY)}#{grp_id}'),
                InlineKeyboardButton('ᴠᴇʀɪꜰʏ' if settings.get("is_verify", IS_VERIFY) else 'ꜱʜᴏʀᴛʟɪɴᴋ', callback_data=f'setgs#is_verify#{settings.get("is_verify", IS_VERIFY)}#{grp_id}')
            ],[
                InlineKeyboardButton('❌ ᴄʟᴏsᴇ ❌', callback_data='close_data')
            ]]
        btn = [[
                InlineKeyboardButton("Oᴘᴇɴ Hᴇʀᴇ ↓", callback_data=f"opnsetgrp#{grp_id}")
            ],[
                InlineKeyboardButton("Oᴘᴇɴ Iɴ PM ⇲", callback_data=f"opnsetpm#{grp_id}")
            ],[
                InlineKeyboardButton('❌ ᴄʟᴏsᴇ ❌', callback_data='close_data')
            ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            await message.reply_text(
                text="<b>Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴏᴘᴇɴ sᴇᴛᴛɪɴɢs ʜᴇʀᴇ ?</b>",
                reply_markup=InlineKeyboardMarkup(btn),
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
            )
        else:
            await message.reply_text(
                text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
            )
            
@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘ...</b>")
    grp_id = message.chat.id
    title = message.chat.title
    invite_link = await client.export_chat_invite_link(grp_id)
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ</b>')
    try:
        template = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("Command Incomplete!")    
    await save_group_settings(grp_id, {'template': template})
    await message.reply_text(f"Successfully changed template for {title} to\n\n{template}", disable_web_page_preview=True)
    await client.send_message(LOG_API_CHANNEL, f"#template for {title} (Group ID: {grp_id}, Invite Link: {invite_link}) has been updated by {message.from_user.username}")
    
@Client.on_message(filters.command('set_caption'))
async def save_caption(client, message):
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ</b>')
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘ...</b>")
    try:
        caption = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("<code>ɢɪᴠᴇ ᴍᴇ ᴀ ᴄᴀᴘᴛɪᴏɴ ᴀʟᴏɴɢ ᴡɪᴛʜ ɪᴛ.\n\nᴇxᴀᴍᴘʟᴇ -\n\nꜰᴏʀ ꜰɪʟᴇ ɴᴀᴍᴇ ꜱᴇɴᴅ <code>{file_name}</code>\nꜰᴏʀ ꜰɪʟᴇ ꜱɪᴢᴇ ꜱᴇɴᴅ <code>{file_size}</code>\n\n<code>/set_caption {file_name}</code></code>")
    await save_group_settings(grp_id, {'caption': caption})
    await message.reply_text(f"Successfully changed caption for {title}\n\nCaption - {caption}", disable_web_page_preview=True)
    await client.send_message(LOG_API_CHANNEL, f"#Caption for {title} (Group ID: {grp_id}) has been updated by {message.from_user.username}")
	
@Client.on_message(filters.command("reload"))
async def reset_group_command(client, message):
    grp_id = message.chat.id
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ</b>')
    sts = await message.reply("<b>♻️ ᴄʜᴇᴄᴋɪɴɢ...</b>")
    await asyncio.sleep(1.2)
    await sts.delete()
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘ...</b>")
    btn = [[
        InlineKeyboardButton('🚫 ᴄʟᴏsᴇ 🚫', callback_data='close_data')
    ]]
    reply_markup = InlineKeyboardMarkup(btn)
    reset_settings = {
        'shortner': SHORTENER_WEBSITE,
        'api': SHORTENER_API,
        'shortner_two': SHORTENER_WEBSITE2,
        'api_two': SHORTENER_API2,
        'verify_time': TWO_VERIFY_GAP,
        'template': IMDB_TEMPLATE,
        'tutorial': TUTORIAL,
        'tutorial_2': TUTORIAL_2,
        'caption': FILE_CAPTION,
        'log': LOG_VR_CHANNEL
    }
    await save_group_settings(grp_id, reset_settings)
    await message.reply_text('ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ʀᴇꜱᴇᴛ ɢʀᴏᴜᴘ ꜱᴇᴛᴛɪɴɢꜱ...', reply_markup=reply_markup)

@Client.on_message(filters.command("send"))
async def send_msg(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('<b>ᴏɴʟʏ ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ...</b>')
        return
    if message.reply_to_message:
        target_ids = message.text.split(" ")[1:]
        if not target_ids:
            await message.reply_text("<b>ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴏɴᴇ ᴏʀ ᴍᴏʀᴇ ᴜꜱᴇʀ ɪᴅꜱ ᴀꜱ ᴀ ꜱᴘᴀᴄᴇ...</b>")
            return
        out = "\n\n"
        success_count = 0
        try:
            users = await db.get_all_users()
            for target_id in target_ids:
                try:
                    user = await bot.get_users(target_id)
                    out += f"{user.id}\n"
                    await message.reply_to_message.copy(int(user.id))
                    success_count += 1
                except Exception as e:
                    out += f"‼️ ᴇʀʀᴏʀ ɪɴ ᴛʜɪꜱ ɪᴅ - <code>{target_id}</code> <code>{str(e)}</code>\n"
            await message.reply_text(f"<b>✅️ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴍᴇꜱꜱᴀɢᴇ ꜱᴇɴᴛ ɪɴ `{success_count}` ɪᴅ\n<code>{out}</code></b>")
        except Exception as e:
            await message.reply_text(f"<b>‼️ ᴇʀʀᴏʀ - <code>{e}</code></b>")
    else:
        await message.reply_text("<b>ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴀꜱ ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇꜱꜱᴀɢᴇ, ꜰᴏʀ ᴇɢ - <code>/send userid1 userid2</code></b>")

@Client.on_message(filters.command("search"))
async def search_files(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('Only the bot owner can use this command... 😑')
        return
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, this command won't work in groups. It only works in my PM!</b>")  
    try:
        keyword = message.text.split(" ", 1)[1]
    except IndexError:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, give me a keyword along with the command to delete files.</b>")
    files, total = await get_bad_files(keyword)
    if int(total) == 0:
        await message.reply_text('<i>I could not find any files with this keyword 😐</i>')
        return 
    file_names = "\n\n".join(f"{index + 1}. {item['file_name']}" for index, item in enumerate(files))
    file_data = f"🚫 Your search - '{keyword}':\n\n{file_names}"    
    with open("file_names.txt", "w" , encoding='utf-8') as file:
        file.write(file_data)
    await message.reply_document(
        document="file_names.txt",
        caption=f"<b>♻️ ʙʏ ʏᴏᴜʀ ꜱᴇᴀʀᴄʜ, ɪ ꜰᴏᴜɴᴅ - <code>{total}</code> ꜰɪʟᴇs</b>",
        parse_mode=enums.ParseMode.HTML
    )
    os.remove("file_names.txt")

@Client.on_message(filters.command("deletefiles"))
async def deletemultiplefiles(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('ᴏɴʟʏ ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ... 😑')
        return
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>ʜᴇʏ {message.from_user.mention}, ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏɴ'ᴛ ᴡᴏʀᴋ ɪɴ ɢʀᴏᴜᴘs. ɪᴛ ᴏɴʟʏ ᴡᴏʀᴋs ᴏɴ ᴍʏ ᴘᴍ !!</b>")
    else:
        pass
    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(f"<b>ʜᴇʏ {message.from_user.mention}, ɢɪᴠᴇ ᴍᴇ ᴀ ᴋᴇʏᴡᴏʀᴅ ᴀʟᴏɴɢ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ꜰɪʟᴇs.</b>")
    files, total = await get_bad_files(keyword)
    if int(total) == 0:
        await message.reply_text('<i>ɪ ᴄᴏᴜʟᴅ ɴᴏᴛ ꜰɪɴᴅ ᴀɴʏ ꜰɪʟᴇs ᴡɪᴛʜ ᴛʜɪs ᴋᴇʏᴡᴏʀᴅ 😐</i>')
        return 
    btn = [[
       InlineKeyboardButton("ʏᴇs, ᴄᴏɴᴛɪɴᴜᴇ ✅", callback_data=f"killfilesak#{keyword}")
       ],[
       InlineKeyboardButton("ɴᴏ, ᴀʙᴏʀᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ 😢", callback_data="close_data")
    ]]
    await message.reply_text(
        text=f"<b>ᴛᴏᴛᴀʟ ꜰɪʟᴇs ꜰᴏᴜɴᴅ - <code>{total}</code>\n\nᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ?\n\nɴᴏᴛᴇ:- ᴛʜɪs ᴄᴏᴜʟᴅ ʙᴇ ᴀ ᴅᴇsᴛʀᴜᴄᴛɪᴠᴇ ᴀᴄᴛɪᴏɴ!!</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("del_file"))
async def delete_files(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('Only the bot owner can use this command... 😑')
        return
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, this command won't work in groups. It only works on my PM!</b>")    
    try:
        keywords = message.text.split(" ", 1)[1].split(",")
    except IndexError:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, give me keywords separated by commas along with the command to delete files.</b>")   
    deleted_files_count = 0
    not_found_files = []
    for keyword in keywords:
        result = await Media.collection.delete_many({'file_name': keyword.strip()})
        if result.deleted_count:
            deleted_files_count += 1
        else:
            not_found_files.append(keyword.strip())
    if deleted_files_count > 0:
        await message.reply_text(f'<b>{deleted_files_count} file successfully deleted from the database 💥</b>')
    if not_found_files:
        await message.reply_text(f'<b>Files not found in the database - <code>{", ".join(not_found_files)}</code></b>')

@Client.on_message(filters.command('set_shortner'))
async def set_shortner(c, m):
    grp_id = m.chat.id
    title = m.chat.title
    if not await is_check_admin(c, grp_id, m.from_user.id):
        return await m.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ</b>')        
    if len(m.text.split()) < 3:
        await m.reply("<b>Use this command like this - \n\n`/set_shortner tnshort.net 06b24eb6bbb025713cd522fb3f696b6d5de11354`</b>")
        return        

    sts = await m.reply("<b>♻️ ᴄʜᴇᴄᴋɪɴɢ...</b>")
    await asyncio.sleep(1.2)
    await sts.delete()

    chat_type = m.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await m.reply_text("<b>ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘ...</b>")

    try:
        logger.info(f"Processing /set_shortner for group {grp_id}")
        URL = m.command[1]
        API = m.command[2]
        
        logger.info(f"Attempting API request to https://{URL}/api?api={API}&url=https://telegram.dog/AV_BOTz_update")
        try:
            resp = requests.get(f'https://{URL}/api?api={API}&url=https://telegram.dog/AV_BOTz_update', timeout=10)
            resp.raise_for_status()
            resp_json = resp.json()
        except requests.exceptions.RequestException as req_err:
            logger.error(f"API request failed: {req_err}")
            raise Exception(f"Failed to validate shortener API: {req_err}")

        if resp_json.get('status') != 'success':
            logger.error(f"API response invalid: {resp_json}")
            raise Exception("Invalid shortener API response")
        SHORT_LINK = resp_json['shortenedUrl']
        logger.info(f"API validated successfully. Short link: {SHORT_LINK}")

        updates = {
            'shortner': URL,
            'api': API
        }
        logger.info(f"Saving settings for group {grp_id}: {updates}")
        await save_group_settings(grp_id, updates)
        
        logger.info(f"Retrieved settings after save for verification")
        settings = await get_settings(grp_id)
        if settings['shortner'] != URL or settings['api'] != API:
            logger.error(f"Settings save verification failed. Expected shortner: {URL}, api: {API}, Got: {settings}")
            raise Exception("Failed to save shortener settings")
        
        await m.reply_text(
            f"<b><u>✓ sᴜᴄᴄᴇssꜰᴜʟʟʏ ʏᴏᴜʀ sʜᴏʀᴛɴᴇʀ ɪs ᴀᴅᴅᴇᴅ</u>\n\n"
            f"ᴅᴇᴍᴏ - {SHORT_LINK}\n\nsɪᴛᴇ - `{URL}`\n\nᴀᴘɪ - `{API}`</b>",
            quote=True
        )
        user_id = m.from_user.id
        user_info = f"@{m.from_user.username}" if m.from_user.username else f"{m.from_user.mention}"
        link = (await c.get_chat(m.chat.id)).invite_link
        grp_link = f"[{m.chat.title}]({link})"
        log_message = f"#New_Shortner_Set_For_1st_Verify\n\nName - {user_info}\nId - `{user_id}`\n\nDomain name - {URL}\nApi - `{API}`\nGroup link - {grp_link}"
        await c.send_message(LOG_API_CHANNEL, log_message, disable_web_page_preview=True)
        logger.info(f"Shortner set successfully for group {grp_id}")

    except Exception as e:
        logger.error(f"Error in /set_shortner for group {grp_id}: {e}")
        updates = {
            'shortner': SHORTENER_WEBSITE,
            'api': SHORTENER_API
        }
        await save_group_settings(grp_id, updates)
        await m.reply_text(
            f"<b><u>💢 ᴇʀʀᴏʀ ᴏᴄᴄᴏᴜʀᴇᴅ!!</u>\n\n"
            f"ᴀᴜᴛᴏ ᴀᴅᴅᴇᴅ ʙᴏᴛ ᴏᴡɴᴇʀ ᴅᴇꜰᴜʟᴛ sʜᴏʀᴛɴᴇʀ\n\n"
            f"ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄʜᴀɴɢᴇ ᴛʜᴇɴ ᴜsᴇ ᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ ᴏʀ ᴀᴅᴅ ᴠᴀʟɪᴅ sʜᴏʀᴛʟɪɴᴋ ᴅᴏᴍᴀɪɴ ɴᴀᴍᴇ & ᴀᴘɪ\n\n"
            f"ʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴄᴏɴᴛᴀᴄᴛ ᴏᴜʀ <a href=https://t.me/AV_SUPPORT_GROUP>sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ</a> ꜰᴏʀ sᴏʟᴠᴇ ᴛʜɪs ɪssᴜᴇ...\n\n"
            f"ʟɪᴋᴇ -\n\n`/set_shortner mdiskshortner.link e7beb3c8f756dfa15d0bec495abc65f58c0dfa95`\n\n"
            f"💔 ᴇʀʀᴏʀ - <code>{e}</code></b>",
            quote=True
        )

@Client.on_message(filters.command('set_shortner_2'))
async def set_shortner_2(c, m):
    grp_id = m.chat.id
    title = m.chat.title
    if not await is_check_admin(c, grp_id, m.from_user.id):
        return await m.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ</b>')
    if len(m.text.split()) < 3:
        await m.reply("<b>Use this command like this - \n\n`/set_shortner_2 tnshort.net 06b24eb6bbb025713cd522fb3f696b6d5de11354`</b>")
        return
    sts = await m.reply("<b>♻️ ᴄʜᴇᴄᴋɪɴɢ...</b>")
    await asyncio.sleep(1.2)
    await sts.delete()
    chat_type = m.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await m.reply_text("<b>ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘ...</b>")
    try:
        URL = m.command[1]
        API = m.command[2]
        resp = requests.get(f'https://{URL}/api?api={API}&url=https://telegram.dog/AV_BOTz_update').json()
        if resp['status'] != 'success':
            raise Exception("Invalid shortener API response")
        SHORT_LINK = resp['shortenedUrl']
        
        # Save both shortner_two and api_two atomically
        updates = {
            'shortner_two': URL,
            'api_two': API
        }
        await save_group_settings(grp_id, updates)
        
        # Verify the save
        settings = await get_settings(grp_id)
        if settings['shortner_two'] != URL or settings['api_two'] != API:
            raise Exception("Failed to save shortener settings")
        
        await m.reply_text(
            f"<b><u>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ʏᴏᴜʀ sʜᴏʀᴛɴᴇʀ ɪs ᴀᴅᴅᴇᴅ</u>\n\n"
            f"ᴅᴇᴍᴏ - {SHORT_LINK}\n\nsɪᴛᴇ - `{URL}`\n\nᴀᴘɪ - `{API}`</b>",
            quote=True
        )
        user_id = m.from_user.id
        user_info = f"@{m.from_user.username}" if m.from_user.username else f"{m.from_user.mention}"
        link = (await c.get_chat(m.chat.id)).invite_link
        grp_link = f"[{m.chat.title}]({link})"
        log_message = f"#New_Shortner_Set_For_2nd_Verify\n\nName - {user_info}\nId - `{user_id}`\n\nDomain name - {URL}\nApi - `{API}`\nGroup link - {grp_link}"
        await c.send_message(LOG_API_CHANNEL, log_message, disable_web_page_preview=True)
    except Exception as e:
        updates = {
            'shortner_two': SHORTENER_WEBSITE2,
            'api_two': SHORTENER_API2
        }
        await save_group_settings(grp_id, updates)
        await m.reply_text(
            f"<b><u>💢 ᴇʀʀᴏʀ ᴏᴄᴄᴏᴜʀᴇᴅ!!</u>\n\n"
            f"ᴀᴜᴛᴏ ᴀᴅᴅᴇᴅ ʙᴏᴛ ᴏᴡɴᴇʀ ᴅᴇꜰᴜʟᴛ sʜᴏʀᴛɴᴇʀ\n\n"
            f"ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄʜᴀɴɢᴇ ᴛʜᴇɴ ᴜsᴇ ᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ ᴏʀ ᴀᴅᴅ ᴠᴀʟɪᴅ sʜᴏʀᴛʟɪɴᴋ ᴅᴏᴍᴀɪɴ ɴᴀᴍᴇ & ᴀᴘɪ\n\n"
            f"ʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴄᴏɴᴛᴀᴄᴛ ᴏᴜʀ <a href=https://t.me/AV_SUPPORT_GROUP>sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ</a> ꜰᴏʀ sᴏʟᴠᴇ ᴛʜɪs ɪssᴜᴇ...\n\n"
            f"ʟɪᴋᴇ -\n\n`/set_shortner_2 mdiskshortner.link e7beb3c8f756dfa15d0bec495abc65f58c0dfa95`\n\n"
            f"💔 ᴇʀʀᴏʀ - <code>{e}</code></b>",
            quote=True
        )

@Client.on_message(filters.command('set_log_channel'))
async def set_log(client, message):
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ</b>')
    if len(message.text.split()) == 1:
        await message.reply("<b>Use this command like this - \n\n`/set_log_channel -100******`</b>")
        return
    sts = await message.reply("<b>♻️ ᴄʜᴇᴄᴋɪɴɢ...</b>")
    await asyncio.sleep(1.2)
    await sts.delete()
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘ...</b>")
    try:
        log = int(message.text.split(" ", 1)[1])
    except IndexError:
        return await message.reply_text("<b><u>ɪɴᴠᴀɪʟᴅ ꜰᴏʀᴍᴀᴛ!!</u>\n\nᴜsᴇ ʟɪᴋᴇ ᴛʜɪs - `/set_log_channel -100xxxxxxxx`</b>")
    except ValueError:
        return await message.reply_text('<b>ᴍᴀᴋᴇ sᴜʀᴇ ɪᴅ ɪs ɪɴᴛᴇɢᴇʀ...</b>')
    try:
        t = await client.send_message(chat_id=log, text="<b>ʜᴇʏ ᴡʜᴀᴛ's ᴜᴘ!!</b>")
        await asyncio.sleep(3)
        await t.delete()
    except Exception as e:
        return await message.reply_text(f'<b><u>😐 ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜɪs ʙᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ...</u>\n\n💔 ᴇʀʀᴏʀ - <code>{e}</code></b>')
    await save_group_settings(grp_id, {'log': log})
    await message.reply_text(f"<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ sᴇᴛ ʏᴏᴜʀ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ꜰᴏʀ {title}\n\nɪᴅ - `{log}`</b>", disable_web_page_preview=True)
    user_id = message.from_user.id
    user_info = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.mention}"
    link = (await client.get_chat(message.chat.id)).invite_link
    grp_link = f"[{message.chat.title}]({link})"
    log_message = f"#New_Log_Channel_Set\n\nName - {user_info}\nId - `{user_id}`\n\nLog channel id - `{log}`\nGroup link - {grp_link}"
    await client.send_message(LOG_API_CHANNEL, log_message, disable_web_page_preview=True)  

@Client.on_message(filters.command('details'))
async def all_settings(client, message):
    grp_id = message.chat.id
    title = message.chat.title
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘ...</b>")
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ</b>')
    settings = await get_settings(grp_id)
    fsub = await db.getFsub(message.chat.id)
    if not settings["is_verify"]:
        text = f"""<b><u>⚙️ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ꜰᴏʀ -</u> {title}

<u>✅️ sʜᴏʀᴛɴᴇʀ ɴᴀᴍᴇ/ᴀᴘɪ</u>
ɴᴀᴍᴇ - `{settings["shortner"]}`
ᴀᴘɪ - `{settings["api"]}`

📍 ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ - {settings['tutorial']}

🌀 ғᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟ - `{fsub}`

🎯 ɪᴍᴅʙ ᴛᴇᴍᴘʟᴀᴛᴇ - `{settings['template']}`

📂 ꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ - `{settings['caption']}`</b>"""
    else:
       text = f"""<b><u>⚙️ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ꜰᴏʀ -</u> {title}

<u>✅️ 1sᴛ ᴠᴇʀɪꜰʏ sʜᴏʀᴛɴᴇʀ ɴᴀᴍᴇ/ᴀᴘɪ</u>
ɴᴀᴍᴇ - `{settings["shortner"]}`
ᴀᴘɪ - `{settings["api"]}`

<u>✅️ 2ɴᴅ ᴠᴇʀɪꜰʏ sʜᴏʀᴛɴᴇʀ ɴᴀᴍᴇ/ᴀᴘɪ</u>
ɴᴀᴍᴇ - `{settings["shortner_two"]}`
ᴀᴘɪ - `{settings["api_two"]}`

🧭 2ɴᴅ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴛɪᴍᴇ - `{settings["verify_time"]}`

📝 ʟᴏɢ ᴄʜᴀɴɴᴇʟ ɪᴅ - `{settings['log']}`

📍 ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ 1 - {settings['tutorial']}

 📍 ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ 2 - {settings.get('tutorial_2', TUTORIAL_2)}

🌀 ғᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟ - `{fsub}`

🎯 ɪᴍᴅʙ ᴛᴇᴍᴘʟᴀᴛᴇ - `{settings['template']}`

📂 ꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ - `{settings['caption']}`</b>"""
    
    btn = [[
        InlineKeyboardButton("ʀᴇꜱᴇᴛ ᴅᴀᴛᴀ", callback_data="reset_grp_data")
    ],[
        InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close_data")
    ]]
    reply_markup=InlineKeyboardMarkup(btn)
    dlt=await message.reply_text(text, reply_markup=reply_markup, disable_web_page_preview=True)
    await asyncio.sleep(300)
    await dlt.delete()

	    
@Client.on_message(filters.command('set_time'))
async def set_time(client, message):
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘ...</b>")       
    grp_id = message.chat.id
    title = message.chat.title
    invite_link = await client.export_chat_invite_link(grp_id)
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ</b>')
    try:
        time = int(message.text.split(" ", 1)[1])
    except:
        return await message.reply_text("<b>ᴄᴏᴍᴍᴀɴᴅ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ\n\nᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ʟɪᴋᴇ ᴛʜɪꜱ - <code>/set_time 600</code> [ ᴛɪᴍᴇ ᴍᴜꜱᴛ ʙᴇ ɪɴ ꜱᴇᴄᴏɴᴅꜱ ]</b>")   
    await save_group_settings(grp_id, {'verify_time': time})
    await message.reply_text(f"<b>✅️ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇᴛ 2ɴᴅ ᴠᴇʀɪꜰʏ ᴛɪᴍᴇ ꜰᴏʀ {title}\n\nᴛɪᴍᴇ - <code>{time}</code></b>")
    await client.send_message(LOG_API_CHANNEL, f"2nd verify time for {title} (Group ID: {grp_id}, Invite Link: {invite_link}) has been updated by {message.from_user.username}")
	
@Client.on_message(filters.command('set_tutorial_2'))
async def set_tutorial_2(client, message):
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ</b>')
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text(f"<b>ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘ...</b>")
    try:
        tutorial = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("<b>Command Incomplete!!\n\nuse like this -</b>\n\n<code>/set_tutorial_2 https://t.me/moviehiap44</code>")
    await save_group_settings(grp_id, {'tutorial_2': tutorial})
    await message.reply_text(f"<b>Successfully changed tutorial for {title}</b>\n\nLink - {tutorial}", disable_web_page_preview=True)
    await client.send_message(LOG_API_CHANNEL, f"#Tutorial_2 for {title} (Group ID: {grp_id}) has been updated by {message.from_user.username}")

@Client.on_message(filters.command('set_tutorial'))
async def set_tutorial(client, message):
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ</b>')
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text(f"<b>ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘ...</b>")
    try:
        tutorial = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("<b>Command Incomplete!!\n\nuse like this -</b>\n\n<code>/set_tutorial https://t.me/moviehiap/42</code>")
    await save_group_settings(grp_id, {'tutorial': tutorial})
    await message.reply_text(f"<b>Successfully changed tutorial for {title}</b>\n\nLink - {tutorial}", disable_web_page_preview=True)
    await client.send_message(LOG_API_CHANNEL, f"#Tutorial for {title} (Group ID: {grp_id}) has been updated by {message.from_user.username}")

@Client.on_message(filters.private & filters.command("pm_search_on"))
async def set_pm_search_on(client, message):
    user_id = message.from_user.id
    bot_id = client.me.id
    if user_id not in ADMINS:
        await message.delete()
        return
    
    await db.update_pm_search_status(bot_id, enable=True)
    await message.reply_text("<b><i>✅️ ᴘᴍ ꜱᴇᴀʀᴄʜ ᴇɴᴀʙʟᴇᴅ, ꜰʀᴏᴍ ɴᴏᴡ ᴜꜱᴇʀꜱ ᴀʙʟᴇ ᴛᴏ ꜱᴇᴀʀᴄʜ ᴍᴏᴠɪᴇ ɪɴ ʙᴏᴛ ᴘᴍ.</i></b>")

@Client.on_message(filters.private & filters.command("pm_search_off"))
async def set_pm_search_off(client, message):
    user_id = message.from_user.id
    bot_id = client.me.id
    if user_id not in ADMINS:
        await message.delete()
        return
    
    await db.update_pm_search_status(bot_id, enable=False)
    await message.reply_text("<b><i>❌️ ᴘᴍ ꜱᴇᴀʀᴄʜ ᴅɪꜱᴀʙʟᴇᴅ, ꜰʀᴏᴍ ɴᴏᴡ ɴᴏ ᴏɴᴇ ᴄᴀɴ ᴀʙʟᴇ ᴛᴏ ꜱᴇᴀʀᴄʜ ᴍᴏᴠɪᴇ ɪɴ ʙᴏᴛ ᴘᴍ.</i></b>")

@Client.on_message(filters.private & filters.command("movie_update_on"))
async def set_send_movie_on(client, message):
    user_id = message.from_user.id
    bot_id = client.me.id
    if user_id not in ADMINS:
        await message.delete()
        return    
    await db.update_send_movie_update_status(bot_id, enable=True)
    await message.reply_text("<b><i>✅️ ꜱᴇɴᴅ ᴍᴏᴠɪᴇ ᴜᴘᴅᴀᴛᴇ ᴇɴᴀʙʟᴇᴅ.</i></b>")

@Client.on_message(filters.private & filters.command("movie_update_off"))
async def set_send_movie_update_off(client, message):
    user_id = message.from_user.id
    bot_id = client.me.id
    if user_id not in ADMINS:
        await message.delete()
        return    
    await db.update_send_movie_update_status(bot_id, enable=False)
    await message.reply_text("<b><i>❌️ ꜱᴇɴᴅ ᴍᴏᴠɪᴇ ᴜᴘᴅᴀᴛᴇ ᴅɪꜱᴀʙʟᴇᴅ.</i></b>")
