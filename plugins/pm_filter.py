import requests
import asyncio
import re
import math
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from pyrogram.types import WebAppInfo
import string
from info import * #NO_RESULTS_MSG, STICKERS_IDS,PREMIUM_POINT,MAX_BTN, BIN_CHANNEL, USERNAME, URL, ADMINS, LANGUAGES,QUALITIES,YEARS,SEASONS, AUTH_CHANNEL, SUPPORT_GROUP, IMDB, IMDB_TEMPLATE, LOG_CHANNEL, LOG_VR_CHANNEL, TUTORIAL, FILE_CAPTION, SHORTENER_WEBSITE, SHORTENER_API, SHORTENER_WEBSITE2, SHORTENER_API2, IS_PM_SEARCH, QR_CODE, DELETE_TIME
from pyrogram.types import *
from pyrogram import Client, filters, enums
from pyrogram.errors import * # FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid, ChatAdminRequired
from utils import temp, get_settings, is_check_admin, is_subscribed, get_status, get_hash, get_name, get_size, save_group_settings, is_subscribed, get_poster, get_status, get_readable_time, imdb, formate_file_name, get_users
from database.users_chats_db import db
from database.config_db import mdb
from database.ia_filterdb import Media, get_search_results, get_bad_files, get_file_details, av_search_results
import random
from database.aman import delete_all_referal_users, get_referal_users_count, get_referal_all_users, referal_add_user
lock = asyncio.Lock()
from .helper.checkFsub import is_user_fsub
BUTTONS = {}
FILES_ID = {}
CAP = {}
REACTION = ["🔥", "❤️", "😍", "⚡", "👍", "👎", "❤", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "❤‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌", "🏆", "🍾", "💋", "🖕", "😈", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝", "✍", "🤗", "🫡", "🎅", "🎄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂", "🤷", "🤷‍♀", "😡"]
import traceback
from fuzzywuzzy import process
	
@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_search(client, message):
    bot_id = client.me.id
    user_id = message.from_user.id
    user = message.from_user.mention
    await message.react(emoji=random.choice(REACTION), big=True)
    content = message.text
    if content.startswith("/") or content.startswith("#"): return  
    if await db.get_pm_search_status(bot_id):
        await auto_filter(client, message)
    else:
        await message.reply_text(
            text="<b>ʜᴇʏ ᴅᴜᴅᴇ 😍 ,\n\nʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ᴍᴏᴠɪᴇs ꜰʀᴏᴍ ʜᴇʀᴇ. ʀᴇǫᴜᴇsᴛ ᴏɴ ᴏᴜʀ <a href=https://t.me/movies_group8>ᴍᴏᴠɪᴇ ɢʀᴏᴜᴘ</a> ᴏʀ ᴄʟɪᴄᴋ ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ👇</b>",   
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📝 ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ ", url=f"https://t.me/movies_group8")]])
	)
	    
    
@Client.on_message(filters.group & filters.text & filters.incoming)
async def group_search(client, message):
  #  await message.react(emoji=random.choice(REACTION), big=True)
    user_id = message.from_user.id if message.from_user else None
    chat_id = message.chat.id
    settings = await get_settings(chat_id)
    ifJoinedFsub = await is_user_fsub(client,message)
    if ifJoinedFsub == False:
        return
    if message.chat.id == SUPPORT_GROUP :
                if message.text.startswith("/"):
                    return
                files, n_offset, total = await get_search_results(message.text, offset=0)
                if total != 0:
                    msg = await message.reply_text(script.SUPPORT_GRP_MOVIE_TEXT.format(message.from_user.mention() , total) ,             reply_markup=InlineKeyboardMarkup([
                        [ InlineKeyboardButton('ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ 😉' , url=f"https://t.me/movies_group7")]
                        ]))
                    await asyncio.sleep(600)
                    return await msg.delete()
                else: return     
    if settings["auto_filter"]:
        if not user_id:
            await message.reply("<b>🚨 ɪ'ᴍ ɴᴏᴛ ᴡᴏʀᴋɪɴɢ ғᴏʀ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ!</b>")
            return
        
        if 'hindi' in message.text.lower() or 'tamil' in message.text.lower() or 'telugu' in message.text.lower() or 'malayalam' in message.text.lower() or 'kannada' in message.text.lower() or 'english' in message.text.lower() or 'gujarati' in message.text.lower(): 
            return await auto_filter(client, message)

        elif message.text.startswith("/"):
            return
        
        elif re.findall(r'https?://\S+|www\.\S+|t\.me/\S+', message.text):
            if await is_check_admin(client, message.chat.id, message.from_user.id):
                return
            await message.delete()
            return await message.reply("<b>sᴇɴᴅɪɴɢ ʟɪɴᴋ ɪsɴ'ᴛ ᴀʟʟᴏᴡᴇᴅ ʜᴇʀᴇ ❌🤞🏻</b>")

        elif '@admin' in message.text.lower() or '@admins' in message.text.lower():
            if await is_check_admin(client, message.chat.id, message.from_user.id):
                return
            admins = []
            async for member in client.get_chat_members(chat_id=message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                if not member.user.is_bot:
                    admins.append(member.user.id)
                    if member.status == enums.ChatMemberStatus.OWNER:
                        if message.reply_to_message:
                            try:
                                sent_msg = await message.reply_to_message.forward(member.user.id)
                                await sent_msg.reply_text(f"#Attention\n★ User: {message.from_user.mention}\n★ Group: {message.chat.title}\n\n★ <a href={message.reply_to_message.link}>Go to message</a>", disable_web_page_preview=True)
                            except:
                                pass
                        else:
                            try:
                                sent_msg = await message.forward(member.user.id)
                                await sent_msg.reply_text(f"#Attention\n★ User: {message.from_user.mention}\n★ Group: {message.chat.title}\n\n★ <a href={message.link}>Go to message</a>", disable_web_page_preview=True)
                            except:
                                pass
            hidden_mentions = (f'[\u2064](tg://user?id={user_id})' for user_id in admins)
            await message.reply_text('<code>Report sent</code>' + ''.join(hidden_mentions))
            return               
        else:
            try: 
                await auto_filter(client, message)
            except Exception as e:
                traceback.print_exc()
                print('found err in grp search  :',e)

    else:
        k=await message.reply_text('<b>⚠️ ᴀᴜᴛᴏ ғɪʟᴛᴇʀ ᴍᴏᴅᴇ ɪꜱ ᴏғғ...</b>')
        await asyncio.sleep(10)
        await k.delete()
        try:
            await message.delete()
        except:
            pass

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    cap = CAP.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
        return
    files, n_offset, total = await get_search_results(search, offset=offset)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0
    if not files:
        return
    temp.FILES_ID[key] = files
    
    batch_ids = files
    temp.FILES_ID[f"{query.message.chat.id}-{query.id}"] = batch_ids
    batch_link = f"batchfiles#{query.message.chat.id}#{query.id}#{query.from_user.id}"

    ads, ads_name, _ = await mdb.get_advirtisment()
    ads_text = ""
    if ads is not None and ads_name is not None:
        ads_url = f"https://t.me/{temp.U_NAME}?start=ads"
        ads_text = f"<a href={ads_url}>{ads_name}</a>"
    ads = f"\n━━━━━━━━━━━━━━━━━━\n <b>{ads_text}</b> \n━━━━━━━━━━━━━━━━━━" if ads_text else ""
    settings = await get_settings(query.message.chat.id)
    reqnxt  = query.from_user.id if query.from_user else 0
    temp.CHAT[query.from_user.id] = query.message.chat.id
    del_msg = f"\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    links = ""
    if settings["link"]:
        btn = []
        for file_num, file in enumerate(files, start=offset+1):
            links += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file.file_id}>[{get_size(file.file_size)}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}</a></b>"""
    else:
        btn = [[InlineKeyboardButton(text=f"📁 {get_size(file.file_size)}≽ {get_name(file.file_name)}", url=f'https://telegram.dog/{temp.U_NAME}?start=file_{query.message.chat.id}_{file.file_id}'),]
                for file in files
              ]
    btn.insert(0,[
        InlineKeyboardButton("‼️ ʟᴀɴɢᴜᴀɢᴇ ‼️", callback_data=f"languages#{key}#{offset}#{req}"),
        ])
    btn.insert(1, [
        InlineKeyboardButton("◖ ǫᴜᴀʟɪᴛʏ ◗", callback_data=f"qualities#{key}#{offset}#{req}"),
           InlineKeyboardButton("◖ sᴇᴀsᴏɴ ◗", callback_data=f"seasons#{key}#{offset}#{req}"),
    ])
    btn.insert(2,[
        InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link),
        InlineKeyboardButton("🥇 ʙᴜʏ", callback_data="seeplans"),
    ])
    if 0 < offset <= int(MAX_BTN):
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - int(MAX_BTN)
    if n_offset == 0:

        btn.append(
            [InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"ᴘᴀɢᴇ {math.ceil(int(offset) / int(MAX_BTN)) + 1} / {math.ceil(total / int(MAX_BTN))}", callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"{math.ceil(int(offset) / int(MAX_BTN)) + 1} / {math.ceil(total / int(MAX_BTN))}", callback_data="pages"),
             InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"{math.ceil(int(offset) / int(MAX_BTN)) + 1} / {math.ceil(total / int(MAX_BTN))}", callback_data="pages"),
                InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    if settings["link"]:
        links = ""
        for file_num, file in enumerate(files, start=offset+1):
            links += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file.file_id}>[{get_size(file.file_size)}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}</a></b>"""
        await query.message.edit_text(cap + links + del_msg + ads, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btn))
        return        
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()
    
@Client.on_callback_query(filters.regex(r"^seasons#"))
async def seasons_cb_handler(client: Client, query: CallbackQuery):
    _, key, offset, req = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True) 
    btn= []
    for i in range(0, len(SEASONS)-1, 3):
        btn.append([
            InlineKeyboardButton(
                text=SEASONS[i].title(),
                callback_data=f"season_search#{SEASONS[i].lower()}#{key}#0#{offset}#{req}"
            ),
            InlineKeyboardButton(
                text=SEASONS[i+1].title(),
                callback_data=f"season_search#{SEASONS[i+1].lower()}#{key}#0#{offset}#{req}"
            ),
            InlineKeyboardButton(
                text=SEASONS[i+2].title(),
                callback_data=f"season_search#{SEASONS[i+2].lower()}#{key}#0#{offset}#{req}"
            ),
        ])

    btn.append([InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{offset}")])
    await query.message.edit_text("<b>ɪɴ ᴡʜɪᴄʜ sᴇᴀsᴏɴ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, ᴄʜᴏᴏsᴇ ғʀᴏᴍ ʜᴇʀᴇ ↓↓</b>", reply_markup=InlineKeyboardMarkup(btn))
    return

@Client.on_callback_query(filters.regex(r"^season_search#"))
async def season_search(client: Client, query: CallbackQuery):
    _, season, key, offset, orginal_offset, req = query.data.split("#")
    seas = int(season.split(' ' , 1)[1])
    if seas < 10:
        seas = f'S0{seas}'
    else:
        seas = f'S{seas}'
    
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)	
    offset = int(offset)
    search = BUTTONS.get(key)
    cap = CAP.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
        return 
    search = search.replace("_", " ")
    files, n_offset, total = await get_search_results(f"{search} {seas}", max_results=int(MAX_BTN), offset=offset)
    files2, n_offset2, total2 = await get_search_results(f"{search} {season}", max_results=int(MAX_BTN), offset=offset)
    total += total2
    try:
        n_offset = int(n_offset)
    except:
        try: 
            n_offset = int(n_offset2)
        except : 
            n_offset = 0
    files = [file for file in files if re.search(seas, file.file_name, re.IGNORECASE)]
    
    if not files:
        files = [file for file in files2 if re.search(season, file.file_name, re.IGNORECASE)]
        if not files:
            await query.answer(f"sᴏʀʀʏ {season.title()} ɴᴏᴛ ғᴏᴜɴᴅ ғᴏʀ {search}", show_alert=1)
            return

    batch_ids = files
    temp.FILES_ID[f"{query.message.chat.id}-{query.id}"] = batch_ids
    batch_link = f"batchfiles#{query.message.chat.id}#{query.id}#{query.from_user.id}"
    ads, ads_name, _ = await mdb.get_advirtisment()
    ads_text = ""
    if ads is not None and ads_name is not None:
        ads_url = f"https://t.me/{temp.U_NAME}?start=ads"
        ads_text = f"<a href={ads_url}>{ads_name}</a>"
    ads = f"\n━━━━━━━━━━━━━━━━━━\n <b>{ads_text}</b> \n━━━━━━━━━━━━━━━━━━" if ads_text else ""
    reqnxt = query.from_user.id if query.from_user else 0
    settings = await get_settings(query.message.chat.id)
    group_id = query.message.chat.id
    temp.CHAT[query.from_user.id] = query.message.chat.id
    del_msg = f"\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    links = ""
    if settings["link"]:
        btn = []
        for file_num, file in enumerate(files, start=offset+1):
            links += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file.file_id}>[{get_size(file.file_size)}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}</a></b>"""
    else:
        btn = [[
                InlineKeyboardButton(text=f"🔗 {get_size(file.file_size)}≽ {get_name(file.file_name)}", callback_data=f'files#{reqnxt}#{file.file_id}'),]
                   for file in files
              ]
        

    btn.insert(1, [
        InlineKeyboardButton("◖ ǫᴜᴀʟɪᴛʏ ◗", callback_data=f"qualities#{key}#{offset}#{req}"),
        InlineKeyboardButton("◖ ʟᴀɴɢᴜᴀɢᴇ ◗", callback_data=f"languages#{key}#{offset}#{req}"),
    ])

    
    if n_offset== '':
        btn.append(
            [InlineKeyboardButton(text="🚸 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs 🚸", callback_data="buttons")]
        )
    elif n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"season_search#{season}#{key}#{offset- int(MAX_BTN)}#{orginal_offset}#{req}"),
             InlineKeyboardButton(f"{math.ceil(offset / int(MAX_BTN)) + 1}/{math.ceil(total / int(MAX_BTN))}", callback_data="pages",),
            ])
    elif offset==0:
        btn.append(
            [InlineKeyboardButton(f"{math.ceil(offset / int(MAX_BTN)) + 1}/{math.ceil(total / int(MAX_BTN))}",callback_data="pages",),
             InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"season_search#{season}#{key}#{n_offset}#{orginal_offset}#{req}"),])
    else:
        btn.append(
            [InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"season_search#{season}#{key}#{offset- int(MAX_BTN)}#{orginal_offset}#{req}"),
             InlineKeyboardButton(f"{math.ceil(offset / int(MAX_BTN)) + 1}/{math.ceil(total / int(MAX_BTN))}", callback_data="pages",),
             InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"season_search#{season}#{key}#{n_offset}#{orginal_offset}#{req}"),])

    btn.append([
        InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{orginal_offset}"),])
    await query.message.edit_text(cap + links + del_msg + ads, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btn))
    return

@Client.on_callback_query(filters.regex(r"^qualities#"))
async def quality_cb_handler(client: Client, query: CallbackQuery):
    _, key, offset, req = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)
    btn= []
    for i in range(0, len(QUALITIES)-1, 3):
        btn.append([
            InlineKeyboardButton(
                text=QUALITIES[i].title(),
                callback_data=f"quality_search#{QUALITIES[i].lower()}#{key}#0#{offset}#{req}"
            ),
            InlineKeyboardButton(
                text=QUALITIES[i+1].title(),
                callback_data=f"quality_search#{QUALITIES[i+1].lower()}#{key}#0#{offset}#{req}"
            ),
            InlineKeyboardButton(
                text=QUALITIES[i+2].title(),
                callback_data=f"quality_search#{QUALITIES[i+2].lower()}#{key}#0#{offset}#{req}"
            ),
        ])
    btn.append([InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{offset}")])
    await query.message.edit_text("<b>ɪɴ ᴡʜɪᴄʜ ǫᴜᴀʟɪᴛʏ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, ᴄʜᴏᴏsᴇ ғʀᴏᴍ ʜᴇʀᴇ ↓↓</b>", reply_markup=InlineKeyboardMarkup(btn))
    return

@Client.on_callback_query(filters.regex(r"^quality_search#"))
async def quality_search(client: Client, query: CallbackQuery):
    _, qul, key, offset, orginal_offset, req = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)	
    offset = int(offset)
    search = BUTTONS.get(key)
    cap = CAP.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
        return 
    search = search.replace("_", " ")
    files, n_offset, total = await get_search_results(f"{search} {qul}", max_results=int(MAX_BTN), offset=offset)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0
    files = [file for file in files if re.search(qul, file.file_name, re.IGNORECASE)]
    if not files:
        await query.answer(f"sᴏʀʀʏ ǫᴜᴀʟɪᴛʏ {qul.title()} ɴᴏᴛ ғᴏᴜɴᴅ ғᴏʀ {search}", show_alert=1)
        return

    batch_ids = files
    temp.FILES_ID[f"{query.message.chat.id}-{query.id}"] = batch_ids
    batch_link = f"batchfiles#{query.message.chat.id}#{query.id}#{query.from_user.id}"
    ads, ads_name, _ = await mdb.get_advirtisment()
    ads_text = ""
    if ads is not None and ads_name is not None:
        ads_url = f"https://t.me/{temp.U_NAME}?start=ads"
        ads_text = f"<a href={ads_url}>{ads_name}</a>"
    ads = f"\n━━━━━━━━━━━━━━━━━━\n <b>{ads_text}</b> \n━━━━━━━━━━━━━━━━━━" if ads_text else ""
    reqnxt = query.from_user.id if query.from_user else 0
    settings = await get_settings(query.message.chat.id)
    group_id = query.message.chat.id
    temp.CHAT[query.from_user.id] = query.message.chat.id
    del_msg = f"\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    links = ""
    if settings["link"]:
        btn = []
        for file_num, file in enumerate(files, start=offset+1):
            links += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file.file_id}>[{get_size(file.file_size)}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}</a></b>"""
    else:
        btn = [[
                InlineKeyboardButton(text=f"🔗 {get_size(file.file_size)}≽ {get_name(file.file_name)}", callback_data=f'files#{reqnxt}#{file.file_id}'),]
                   for file in files
              ]
        

    btn.insert(0,[
        InlineKeyboardButton("◖ ʟᴀɴɢᴜᴀɢᴇ ◗", callback_data=f"languages#{key}#{offset}#{req}"),
	InlineKeyboardButton("◖ sᴇᴀsᴏɴ ◗", callback_data=f"seasons#{key}#{offset}#{req}"),
        ])
    
    if n_offset== '':
        btn.append(
            [InlineKeyboardButton(text="🚸 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs 🚸", callback_data="buttons")]
        )
    elif n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"quality_search#{qul}#{key}#{offset- int(MAX_BTN)}#{orginal_offset}#{req}"),
             InlineKeyboardButton(f"{math.ceil(offset / int(MAX_BTN)) + 1}/{math.ceil(total / int(MAX_BTN))}", callback_data="pages",),
            ])
    elif offset==0:
        btn.append(
            [InlineKeyboardButton(f"{math.ceil(offset / int(MAX_BTN)) + 1}/{math.ceil(total / int(MAX_BTN))}",callback_data="pages",),
             InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"quality_search#{qul}#{key}#{n_offset}#{orginal_offset}#{req}"),])
    else:
        btn.append(
            [InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"quality_search#{qul}#{key}#{offset- int(MAX_BTN)}#{orginal_offset}#{req}"),
             InlineKeyboardButton(f"{math.ceil(offset / int(MAX_BTN)) + 1}/{math.ceil(total / int(MAX_BTN))}", callback_data="pages",),
             InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"quality_search#{qul}#{key}#{n_offset}#{orginal_offset}#{req}"),])

    btn.append([
        InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{orginal_offset}"),])
    await query.message.edit_text(cap + links + del_msg + ads, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btn))
    return
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):
    _, key, offset, req = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)
    btn  = []
    for i in range(0, len(LANGUAGES)-1, 2):
        btn.append([
            InlineKeyboardButton(
                text=LANGUAGES[i].title(),
                callback_data=f"lang_search#{LANGUAGES[i].lower()}#{key}#0#{offset}#{req}"
            ),
            InlineKeyboardButton(
                text=LANGUAGES[i+1].title(),
                callback_data=f"lang_search#{LANGUAGES[i+1].lower()}#{key}#0#{offset}#{req}"
            ),
                    ])
    
    # btn = [[
    #     InlineKeyboardButton(text=lang.title(), callback_data=f"lang_search#{lang.lower()}#{key}#0#{offset}#{req}"),
    # ]
    #     for lang in LANGUAGES
    # ]
    btn.append([InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{offset}")])
    await query.message.edit_text("<b>ɪɴ ᴡʜɪᴄʜ ʟᴀɴɢᴜᴀɢᴇ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, ᴄʜᴏᴏsᴇ ғʀᴏᴍ ʜᴇʀᴇ ↓↓</b>", reply_markup=InlineKeyboardMarkup(btn))
    return

@Client.on_callback_query(filters.regex(r"^lang_search#"))
async def lang_search(client: Client, query: CallbackQuery):
    _, lang, key, offset, orginal_offset, req = query.data.split("#")
    lang2 = lang[:3]
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)	
    offset = int(offset)
    search = BUTTONS.get(key)
    cap = CAP.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
        return 
    search = search.replace("_", " ")
    files, n_offset, total = await get_search_results(f"{search} {lang}", max_results=int(MAX_BTN), offset=offset)
    files2, n_offset2, total2 = await get_search_results(f"{search} {lang2}", max_results=int(MAX_BTN), offset=offset)
    total += total2
    try:
        n_offset = int(n_offset)
    except:
        try: 
            n_offset = int(n_offset2)
        except : 
            n_offset = 0
    files = [file for file in files if re.search(lang, file.file_name, re.IGNORECASE)]
    if not files:
        files = [file for file in files2 if re.search(lang2, file.file_name, re.IGNORECASE)]
        if not files:
            return await query.answer(f"sᴏʀʀʏ ʟᴀɴɢᴜᴀɢᴇ {lang.title()} ɴᴏᴛ ғᴏᴜɴᴅ ғᴏʀ {search}", show_alert=1)

    batch_ids = files
    temp.FILES_ID[f"{query.message.chat.id}-{query.id}"] = batch_ids
    batch_link = f"batchfiles#{query.message.chat.id}#{query.id}#{query.from_user.id}"
    ads, ads_name, _ = await mdb.get_advirtisment()
    ads_text = ""
    if ads is not None and ads_name is not None:
        ads_url = f"https://t.me/{temp.U_NAME}?start=ads"
        ads_text = f"<a href={ads_url}>{ads_name}</a>"
    ads = f"\n━━━━━━━━━━━━━━━━━━\n <b>{ads_text}</b> \n━━━━━━━━━━━━━━━━━━" if ads_text else ""
    reqnxt = query.from_user.id if query.from_user else 0
    settings = await get_settings(query.message.chat.id)
    group_id = query.message.chat.id
    temp.CHAT[query.from_user.id] = query.message.chat.id
    del_msg = f"\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    links = ""
    if settings["link"]:
        btn = []
        for file_num, file in enumerate(files, start=offset+1):
            links += f"""\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file.file_id}>[{get_size(file.file_size)}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}</a></b>"""
    else:
        btn = [[
                InlineKeyboardButton(text=f"🔗 {get_size(file.file_size)}≽ {get_name(file.file_name)}", callback_data=f'files#{reqnxt}#{file.file_id}'),]
                   for file in files
              ]
        

    btn.insert(0,[
        InlineKeyboardButton("◖ ǫᴜᴀʟɪᴛʏ ◗", callback_data=f"qualities#{key}#{offset}#{req}"),
        InlineKeyboardButton("◖ sᴇᴀsᴏɴ ◗", callback_data=f"seasons#{key}#{offset}#{req}"),
	])

    if n_offset== '':
        btn.append(
            [InlineKeyboardButton(text="🚸 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs 🚸", callback_data="buttons")]
        )
    elif n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"lang_search#{lang}#{key}#{offset- int(MAX_BTN)}#{orginal_offset}#{req}"),
             InlineKeyboardButton(f"{math.ceil(offset / int(MAX_BTN)) + 1}/{math.ceil(total / int(MAX_BTN))}", callback_data="pages",),
            ])
    elif offset==0:
        btn.append(
            [InlineKeyboardButton(f"{math.ceil(offset / int(MAX_BTN)) + 1}/{math.ceil(total / int(MAX_BTN))}",callback_data="pages",),
             InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"lang_search#{lang}#{key}#{n_offset}#{orginal_offset}#{req}"),])
    else:
        btn.append(
            [InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"lang_search#{lang}#{key}#{offset- int(MAX_BTN)}#{orginal_offset}#{req}"),
             InlineKeyboardButton(f"{math.ceil(offset / int(MAX_BTN)) + 1}/{math.ceil(total / int(MAX_BTN))}", callback_data="pages",),
             InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"lang_search#{lang}#{key}#{n_offset}#{orginal_offset}#{req}"),])

    btn.append([
        InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{orginal_offset}"),])
    await query.message.edit_text(cap + links + del_msg + ads, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btn))
    return
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex(r"^spol"))
async def pm_spoll_choker(bot, query):
    _, id, user = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    movie = await get_poster(id, id=True)
    search = movie.get('title')
    await query.answer('ᴄʜᴇᴄᴋɪɴɢ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀꜱᴇ 🌚')
    files, offset, total_results = await av_search_results(query.message.chat.id, search)
    if files:
        k = (search, files, offset, total_results)
        await auto_filter(bot, query, k)
    else:
        try:
            reqstr1 = query.from_user.id if query.from_user else 0
            reqstr = await bot.get_users(reqstr1)
            if NO_RESULTS_MSG:
                safari = [[
                    InlineKeyboardButton('ɴᴏᴛ ʀᴇʟᴇᴀsᴇ 📅', callback_data=f"not_release:{reqstr1}:{search}"),
                    InlineKeyboardButton('ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ 🙅', callback_data=f"not_available:{reqstr1}:{search}")
                ],[
                    InlineKeyboardButton('ᴜᴘʟᴏᴀᴅᴇᴅ ✅', callback_data=f"uploaded:{reqstr1}:{search}")
                ],[
                    InlineKeyboardButton('ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ🙅', callback_data=f"series:{reqstr1}:{search}"),
                    InlineKeyboardButton('sᴇʟʟ ᴍɪsᴛᴇᴋ✍️', callback_data=f"spelling_error:{reqstr1}:{search}")
                ],[
                    InlineKeyboardButton('⁉️ Close ⁉️', callback_data=f"close_data")
                ]]
                reply_markup = InlineKeyboardMarkup(safari)
                total=await bot.get_chat_members_count(query.message.chat.id)
                await bot.send_message(chat_id=LOG_VR_CHANNEL, text=(script.NORSLTS.format(query.message.chat.title, query.message.chat.id, total, temp.B_NAME, reqstr.mention, search)), reply_markup=InlineKeyboardMarkup(safari))
            k = await query.message.edit(script.MVE_NT_FND)
            await asyncio.sleep(60)
            await k.delete()
            try:
                await query.message.reply_to_message.delete()
            except:
                pass
        except Exception as e:
            reqstr1 = query.from_user.id if query.from_user else 0
            reqstr = await bot.get_users(reqstr1)
            if NO_RESULTS_MSG:
                safari = [[
                    InlineKeyboardButton('ɴᴏᴛ ʀᴇʟᴇᴀsᴇ 📅', callback_data=f"not_release:{reqstr1}:{search}"),
                    InlineKeyboardButton('ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ 🙅', callback_data=f"not_available:{reqstr1}:{search}")
                ],[
                    InlineKeyboardButton('ᴜᴘʟᴏᴀᴅᴇᴅ ✅', callback_data=f"uploaded:{reqstr1}:{search}")
                ],[
                    InlineKeyboardButton('ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ🙅', callback_data=f"series:{reqstr1}:{search}"),
                    InlineKeyboardButton('sᴇʟʟ ᴍɪsᴛᴇᴋ✍️', callback_data=f"spelling_error:{reqstr1}:{search}")
                ],[
                    InlineKeyboardButton('⦉ ᴄʟᴏsᴇ ⦊️', callback_data=f"close_data")
                ]]
                reply_markup = InlineKeyboardMarkup(safari)
                await bot.send_message(chat_id=LOG_VR_CHANNEL, text=(script.PMNORSLTS.format(temp.B_NAME, reqstr.mention, search)), reply_markup=InlineKeyboardMarkup(safari))
            k = await query.message.edit(script.MVE_NT_FND)
            await asyncio.sleep(60)
            await k.delete()
            try:
                await query.message.reply_to_message.delete()
            except:
                pass
		    
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        try:
            user = query.message.reply_to_message.from_user.id
        except:
            user = query.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(script.ALRT_TXT, show_alert=True)
        await query.answer("ᴛʜᴀɴᴋs ꜰᴏʀ ᴄʟᴏsᴇ 🙈")
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type
        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()
        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)    


    elif query.data.startswith("checksub"):
        ident, kk, file_id = query.data.split("#")  
        if AUTH_CHANNEL:
            btn = await is_subscribed(client, query, AUTH_CHANNEL)
            if btn:
                await query.answer(
                    f"👋 Hello {query.from_user.first_name},\n\n"
                    "Yᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ᴀʟʟ ʀᴇǫᴜɪʀᴇᴅ ᴜᴘᴅᴀᴛᴇ Cʜᴀɴɴᴇʟs.\n"
                    "Pʟᴇᴀsᴇ ᴊᴏɪɴ ᴇᴀᴄʜ ᴄʜᴀɴɴᴇʟ ʟɪsᴛᴇᴅ ʙᴇʟᴏᴡ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.\n\n",
                    show_alert=True
                )
                btn.append([InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ ♻️", callback_data=f"checksub#{kk}#{file_id}")])
                await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
                return
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start={kk}_{file_id}")
        await query.message.delete()
	    
    elif query.data.startswith("opnsetpm"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
        #if (
              #  st.status != enums.ChatMemberStatus.ADMINISTRATOR
              #  and st.status != enums.ChatMemberStatus.OWNER
               # and str(userid) not in ADMINS
        #):
            await query.answer("Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        btn2 = [[
                 InlineKeyboardButton("Cʜᴇᴄᴋ PM", url=f"t.me/{temp.U_NAME}")
               ]]
        reply_markup = InlineKeyboardMarkup(btn2)
        await query.message.edit_text(f"<b>Yᴏᴜʀ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ ғᴏʀ {title} ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ʏᴏᴜʀ PM</b>")
        await query.message.edit_reply_markup(reply_markup)
        if settings is not None:
            buttons = [[
                InlineKeyboardButton('ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✓' if settings["auto_filter"] else 'ᴏғғ ✗', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}')
            ],[
                InlineKeyboardButton('ꜰɪʟᴇ sᴇᴄᴜʀᴇ', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✓' if settings["file_secure"] else 'ᴏғғ ✗', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}')
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
                InlineKeyboardButton('ᴠᴇʀɪꜰʏ', callback_data=f'setgs#is_verify#{settings["is_verify"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✅' if settings["is_verify"] else 'ᴏғғ ❌', callback_data=f'setgs#is_verify#{settings["is_verify"]}#{grp_id}')
            ],[  
                InlineKeyboardButton('❌ ᴄʟᴏsᴇ ❌', callback_data='close_data')
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await client.send_message(
                chat_id=userid,
                text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=query.message.id
	    )
    elif query.data.startswith("opnsetgrp"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
        #if (
                #st.status != enums.ChatMemberStatus.ADMINISTRATOR
              #  and st.status != enums.ChatMemberStatus.OWNER
                #and str(userid) not in ADMINS
      #  ):
            await query.answer("Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        if settings is not None:
            buttons = [[
		InlineKeyboardButton('ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✓' if settings["auto_filter"] else 'ᴏғғ ✗', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}')
            ],[
                InlineKeyboardButton('ꜰɪʟᴇ sᴇᴄᴜʀᴇ', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✓' if settings["file_secure"] else 'ᴏғғ ✗', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}')
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
                InlineKeyboardButton('ᴠᴇʀɪꜰʏ', callback_data=f'setgs#is_verify#{settings["is_verify"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✅' if settings["is_verify"] else 'ᴏғғ ❌', callback_data=f'setgs#is_verify#{settings["is_verify"]}#{grp_id}')
            ],[  
                InlineKeyboardButton('❌ ᴄʟᴏsᴇ ❌', callback_data='close_data')
	    ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML
            )
            await query.message.edit_reply_markup(reply_markup)

    elif query.data.startswith("not_available"):
        _, user_id, movie = query.data.split(":")
        try:
            safari = [[
                    InlineKeyboardButton(text=f"🗑 Delete Log ❌", callback_data = "close_data")
                    ]]
            reply_markup = InlineKeyboardMarkup(safari)
            await client.send_message(int(user_id), script.NOT_AVAILABLE_TXT.format(movie),parse_mode=enums.ParseMode.HTML)
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : Nᴏᴛ Aᴠᴀɪʟᴀʙʟᴇ 😒.\n🪪ᴜꜱᴇʀɪᴅ : `{user_id}`\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
        except Exception as e:
            print(e)
            await query.answer(f"{e}", show_alert=True)
            return
    elif query.data.startswith("uploaded"):
        _, user_id, movie = query.data.split(":")
        try:
            safari = [[
                    InlineKeyboardButton(text=f"🗑 Delete Log ❌", callback_data = "close_data")
                    ]]
            reply_markup = InlineKeyboardMarkup(safari)
            await client.send_message(int(user_id), script.UPLOADED_TXT.format(movie),parse_mode=enums.ParseMode.HTML)
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : Uᴘʟᴏᴀᴅᴇᴅ 🎊.\n🪪ᴜꜱᴇʀɪᴅ : `{user_id}`\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
        except Exception as e:
            print(e)
            await query.answer(f"{e}", show_alert=True)
            return
    elif query.data.startswith("not_release"):
        _, user_id, movie = query.data.split(":")
        try:
            safari = [[
                    InlineKeyboardButton(text=f"🗑 Delete Log ❌", callback_data = "close_data")
                    ]]
            reply_markup = InlineKeyboardMarkup(safari)
            await client.send_message(int(user_id), script.NOT_RELEASE_TXT.format(movie),parse_mode=enums.ParseMode.HTML)
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : ɴᴏᴛ ʀᴇʟᴇᴀsᴇ 🙅.\n🪪ᴜꜱᴇʀɪᴅ : `{user_id}`\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
        except Exception as e:
            print(e)
            await query.answer(f"{e}", show_alert=True)
            return
    elif query.data.startswith("spelling_error"):
        _, user_id, movie = query.data.split(":")
        try:
            safari = [[
                    InlineKeyboardButton(text=f"🗑 Delete Log ❌", callback_data = "close_data")
                    ]]
            reply_markup = InlineKeyboardMarkup(safari)
            await client.send_message(int(user_id), script.SPELL_TXT.format(movie),parse_mode=enums.ParseMode.HTML)
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : Sᴘᴇʟʟɪɴɢ Eʀʀᴏʀ 🕵️.\n🪪ᴜꜱᴇʀɪᴅ : `{user_id}`\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
        except Exception as e:
            print(e)
            await query.answer(f"{e}", show_alert=True)
            return
    elif query.data.startswith("series"):
        _, user_id, movie = query.data.split(":")
        try:
            safari = [[
                    InlineKeyboardButton(text=f"🗑 Delete Log ❌", callback_data = "close_data")
                    ]]
            reply_markup = InlineKeyboardMarkup(safari)
            await client.send_message(int(user_id), script.SERIES_FORMAT_TXT.format(movie),parse_mode=enums.ParseMode.HTML)
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : Sᴇʀɪᴇs Eʀʀᴏʀ 🕵️.\n🪪ᴜꜱᴇʀɪᴅ : `{user_id}`\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
        except Exception as e:
            print(e) 
            await query.answer(f"{e}", show_alert=True)
            return
		
    elif query.data.startswith("stream"):
        user_id = query.from_user.id
        file_id = query.data.split('#', 1)[1]
       # STREAM_LINK = await db.get_stream_link()
        AV = await client.send_cached_media(
            chat_id=BIN_CHANNEL,
            file_id=file_id)
        online = f"{URL}/watch/{AV.id}?hash={get_hash(AV)}"
        download = f"{URL}/{AV.id}?hash={get_hash(AV)}"
	    
        await query.message.edit_reply_markup(
            InlineKeyboardMarkup([[
            InlineKeyboardButton("📺 ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ", url=online),
            InlineKeyboardButton("ꜰᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ 🚀", url=download)
      #],[
           # InlineKeyboardButton('🤩 Watch on Telegram 🧿', web_app=WebAppInfo(url=online))
        ]]))
		
    elif query.data == "buttons":
        await query.answer("ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs 😊", show_alert=True)

    elif query.data == "pages":
        await query.answer("ᴛʜɪs ɪs ᴘᴀɢᴇs ʙᴜᴛᴛᴏɴ 😅")

    elif query.data.startswith("lang_art"):
        _, lang = query.data.split("#")
        await query.answer(f"ʏᴏᴜ sᴇʟᴇᴄᴛᴇᴅ {lang.title()} ʟᴀɴɢᴜᴀɢᴇ ⚡️", show_alert=True)


    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs ⇆', url=f'http://t.me/{temp.U_NAME}?startgroup=start')
        ],[
            InlineKeyboardButton('🔖 ᴄᴏᴍᴍᴀɴᴅs ', callback_data='commands'),
	    InlineKeyboardButton('🎁 ᴘᴀɪᴅ ᴘʀᴏᴍᴏᴛɪᴏɴ ', callback_data="avads")
        ],[
	    InlineKeyboardButton('ꜰʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ ✨', callback_data="subscription"),
            InlineKeyboardButton('✘ ᴀʙᴏᴜᴛ ', callback_data='about')
	],[
            InlineKeyboardButton('☢️ ᴇᴀʀɴɴ ᴍᴏɴᴇʏ ᴡɪᴛʜ ʙᴏᴛ ☢️', callback_data='earn')
        ],[
            InlineKeyboardButton('💸 ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ : ʀᴇᴍᴏᴠᴇ ᴀᴅꜱ 💸', callback_data="premium_info"),
        ]]    
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(START_IMG))
        )
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, get_status(), query.from_user.id),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )     

    elif query.data == "purchase":
        buttons = [[
            InlineKeyboardButton('💵 ᴘᴀʏ ᴠɪᴀ ᴜᴘɪ ɪᴅ 💵', callback_data='upi_info')
        ],[
            InlineKeyboardButton('📸 ꜱᴄᴀɴ ǫʀ ᴄᴏᴅᴇ 📸', callback_data='qr_info')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.PURCHASE_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "upi_info":
        buttons = [[
            InlineKeyboardButton('📲 ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ʜᴇʀᴇ', user_id=int(6093349648))
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='purchase')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.UPI_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "qr_info":
        buttons = [[
            InlineKeyboardButton('📲 ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ʜᴇʀᴇ', user_id=int(6093349648))
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='purchase')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(QR_CODE)
	)
        await query.message.edit_text(
            text=script.QR_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
	)

    elif query.data == "premium_info":
        buttons = [[
            InlineKeyboardButton('• ʙʀᴏɴᴢᴇ •', callback_data='broze'),
            InlineKeyboardButton('• ꜱɪʟᴠᴇʀ •', callback_data='silver')
        ],[
            InlineKeyboardButton('• ɢᴏʟᴅ •', callback_data='gold'),
            InlineKeyboardButton('• ᴘʟᴀᴛɪɴᴜᴍ •', callback_data='platinum')
        ],[
            InlineKeyboardButton('• ᴅɪᴀᴍᴏɴᴅ •', callback_data='diamond'),
            InlineKeyboardButton('• ᴏᴛʜᴇʀ •', callback_data='other')
        ],[            
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='start')
        ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.PLAN_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "free":
        buttons = [[
            InlineKeyboardButton('⚜️ ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ꜰʀᴇᴇ ᴛʀɪᴀʟ', callback_data="give_trial")
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='other'),
            InlineKeyboardButton('1 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='broze')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.FREE_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
		)
    elif query.data == "broze":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='other'),
            InlineKeyboardButton('1 / 6', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='silver')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BRONZE_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "silver":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='broze'),
            InlineKeyboardButton('2 / 6', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='gold')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SILVER_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "gold":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='silver'),
            InlineKeyboardButton('3 / 6', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='platinum')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GOLD_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "platinum":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='gold'),
            InlineKeyboardButton('4 / 6', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='diamond')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.PLATINUM_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    
    elif query.data == "diamond":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='platinum'),
            InlineKeyboardButton('5 / 6', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='other')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.DIAMOND_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "other":
        buttons = [[
            InlineKeyboardButton('☎️ ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ', user_id=int(6093349648))
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='diamond'),
            InlineKeyboardButton('6 / 6', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='broze')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.OTHER_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
	    )
	

    elif query.data == "commands":
        buttons = [[
	    InlineKeyboardButton('ᴀᴅᴍɪɴ ᴄᴍᴅ', callback_data='admincmd')
	],[
            InlineKeyboardButton('ɢʀᴏᴜᴘ sᴇᴛᴜᴘ ✍️', callback_data='tts'),
            InlineKeyboardButton('🆎️ ғᴏɴᴛ', callback_data='font')    
        ],[
            InlineKeyboardButton('• ʀᴜʟᴇs •', callback_data='RULES'),
            InlineKeyboardButton('📸 ᴛ-ɢʀᴀᴘʜ', callback_data='telegraph')
	],[
	    InlineKeyboardButton('⋞ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ', callback_data='start')
        ]] 
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(                     
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "admincmd":
        #if user isnt admin then return
        if not query.from_user.id in ADMINS:
            return await query.answer('This Feature Is Only For Admins !' , show_alert=True)
        buttons = [
            [InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='commands')],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_CMD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
	    
    elif query.data == "RULES":
        #add back button
        buttons = [[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='commands')
	]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.RULES_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
	    
    elif query.data == "tts":
        buttons = [[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='commands'),
        ]]
        await query.message.edit_text(
            text=script.TTS_TXT,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
	)
       
    elif query.data == "earn":
        buttons = [[
		InlineKeyboardButton('SETTINGS', callback_data='SETTINGS_T'),
            InlineKeyboardButton('HELP', callback_data='HELP_T')    
        ],
        [
            InlineKeyboardButton('⋞ ʜᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', user_id = ADMINS[0] ),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
             text=script.MONEY_TXT.format(temp.U_NAME, temp.B_NAME),
             reply_markup=reply_markup,
             parse_mode=enums.ParseMode.HTML
		)

    elif query.data == "avads":
        buttons = [[
            InlineKeyboardButton('⋞ ʜᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', user_id = ADMINS[0] ),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
             text=script.AVADS_TXT.format(temp.B_LINK),
             reply_markup=reply_markup,
             parse_mode=enums.ParseMode.HTML
	)

    elif query.data == "SETTINGS_T":
        buttons = [[
		InlineKeyboardButton('HELP', callback_data='HELP_T')  
	],[
            InlineKeyboardButton('⋞ ʜᴏᴍᴇ', callback_data='earn')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
             text=script.SETTINGS_TEXT.format(temp.B_LINK),
             reply_markup=reply_markup,
             parse_mode=enums.ParseMode.HTML
	)

    elif query.data == "HELP_T":
        buttons = [[
		InlineKeyboardButton('SETTINGS', callback_data='SETTINGS_T')
	],[
            InlineKeyboardButton('⋞ ʜᴏᴍᴇ', callback_data='earn')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
             text=script.HELP2_TEXT.format(temp.B_LINK),
             reply_markup=reply_markup,
             parse_mode=enums.ParseMode.HTML
	)
	    
    elif query.data == "disclaimer":
            btn = [[
                    InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ', callback_data='start')
                  ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_text(
                text=(script.DISCLAIMER_TXT),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML 
	    )

    elif query.data == "about":
        buttons = [[
            #InlineKeyboardButton('⌬ Mᴏᴠɪᴇ Gʀᴏᴜᴘ', callback_data="group_info")
	    InlineKeyboardButton('‼️ ᴅɪꜱᴄʟᴀɪᴍᴇʀ ‼️', callback_data='disclaimer')
        ],[
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('• ᴏᴡɴᴇʀ •', user_id=int(6093349648))
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TEXT.format(temp.B_NAME, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
	)

    elif query.data == "seeplans":
        btn = [[
            InlineKeyboardButton('🍁 𝗖𝗹𝗶𝗰𝗸 𝗔𝗹𝗹 𝗣𝗹𝗮𝗻𝘀 & 𝗣𝗿𝗶𝗰𝗲𝘀 🍁', callback_data='premium_info')
        ],[
            InlineKeyboardButton('• 𝗖𝗹𝗼𝘀𝗲 •', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(btn)
        m=await query.message.reply_sticker("CAACAgQAAxkBAAEiLZ9l7VMuTY7QHn4edR6ouHUosQQ9gwACFxIAArzT-FOmYU0gLeJu7x4E") 
        await m.delete()
        await query.message.reply_photo(
            photo=(QR_CODE),
            caption=script.PREPLANS_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
	)

    elif query.data == "seerefer":
      #  m = await message.reply_text(f"<b>Generating Your Refferal Link...</b>")
      #  await m.delete()
        actual_referral_count = await get_referal_users_count(query.from_user.id)
        btn = [[
	    InlineKeyboardButton('invite link', url=f'https://telegram.me/share/url?url=https://t.me/{temp.U_NAME}?start=reff_{query.from_user.id}&text=Hello%21%20Experience%20a%20bot%20that%20offers%20a%20vast%20library%20of%20unlimited%20movies%20and%20series.%20%F0%9F%98%83'),
        InlineKeyboardButton(f'⏳ {actual_referral_count}', callback_data='show_referral_count'),
        InlineKeyboardButton('Cʟᴏsᴇ', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(btn)
        m = await query.message.reply_text(f"<b>Generating Your Refferal Link...</b>") 
        await m.delete()
        await query.message.reply_photo(
            photo=(REFER_PICS),
            caption=script.REFER_TXT.format(temp.U_NAME, query.from_user.id),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
	)
	    
    elif query.data == "show_referral_count":
        actual_referral_count = await get_referal_users_count(query.from_user.id)
        await query.answer(f"Yᴏᴜʀ Pᴏɪɴᴛs : {actual_referral_count}", show_alert=True)  
         
    elif query.data == "subscription":
        actual_referral_count = await get_referal_users_count(query.from_user.id)
        buttons = [[
            InlineKeyboardButton(f'Yᴏᴜʀ Pᴏɪɴᴛs ⏳ {actual_referral_count}', callback_data='show_referral_count'),
                InlineKeyboardButton('Share Link', url=f"https://t.me/share/url?url=https://t.me/{temp.U_NAME}?start=reff_{query.from_user.id}"),
            ],[
                InlineKeyboardButton('⟸ ʙᴀᴄᴋ', callback_data='start'),
                InlineKeyboardButton('✘ Cʟᴏꜱᴇ', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SUBSCRIPTION_TXT.format(REFERAL_PREMEIUM_TIME, temp.U_NAME, query.from_user.id, REFERAL_COUNT),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
	)

    elif query.data == "telegraph":
        buttons = [[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='commands')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)  
        await query.message.edit_text(
            text=script.TELE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "font":
        buttons = [[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='commands')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons) 
        await query.message.edit_text(
            text=script.FONT_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
	)
  
    elif query.data == "all_files_delete":
        files = await Media.count_documents()
        await query.answer('Deleting...')
        await Media.collection.drop()
        await query.message.edit_text(f"Successfully deleted {files} files")
        
    elif query.data.startswith("killfilesak"):
        ident, keyword = query.data.split("#")
        await query.message.edit_text(f"<b>ꜰᴇᴛᴄʜɪɴɢ ꜰɪʟᴇs ꜰᴏʀ ʏᴏᴜʀ ǫᴜᴇʀʏ {keyword} ᴏɴ ᴅʙ...\n\nᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
        files, total = await get_bad_files(keyword)
        await query.message.edit_text(f"<b>ꜰᴏᴜɴᴅ {total} ꜰɪʟᴇs ꜰᴏʀ ʏᴏᴜʀ ǫᴜᴇʀʏ {keyword}!!</b>")
        deleted = 0
        async with lock:
            try:
                for file in files:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media.collection.delete_one({
                        '_id': file_ids,
                    })
                    if result.deleted_count:
                        print(f'Successfully deleted {file_name} from database.')
                    deleted += 1
                    if deleted % 20 == 0:
                        await query.message.edit_text(f"<b>Process started for deleting files from DB. Successfully deleted {str(deleted)} files from DB for your query {keyword} !\n\nPlease wait...</b>")
            except Exception as e:
                print(e)
                await query.message.edit_text(f'Error: {e}')
            else:
                await query.message.edit_text(f"<b>Process Completed for file deletion !\n\nSuccessfully deleted {str(deleted)} files from database for your query {keyword}.</b>")
    elif query.data.startswith("reset_grp_data"):
        grp_id = query.message.chat.id
        btn = [[
            InlineKeyboardButton('☕️ ᴄʟᴏsᴇ ☕️', callback_data='close_data')
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        await save_group_settings(grp_id, 'shortner', SHORTENER_WEBSITE)
        await save_group_settings(grp_id, 'api', SHORTENER_API)
        await save_group_settings(grp_id, 'shortner_two', SHORTENER_WEBSITE2)
        await save_group_settings(grp_id, 'api_two', SHORTENER_API2)
        await save_group_settings(grp_id, 'verify_time', TWO_VERIFY_GAP)
        await save_group_settings(grp_id, 'template', IMDB_TEMPLATE)
        await save_group_settings(grp_id, 'tutorial', TUTORIAL)
        await save_group_settings(grp_id, 'tutorial_2', TUTORIAL_2)
        await save_group_settings(grp_id, 'caption', FILE_CAPTION)
        await save_group_settings(grp_id, 'fsub', AUTH_CHANNEL)
        await save_group_settings(grp_id, 'log', LOG_VR_CHANNEL)
        await query.answer('ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ʀᴇꜱᴇᴛ...')
        await query.message.edit_text("<b>ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ʀᴇꜱᴇᴛ ɢʀᴏᴜᴘ ꜱᴇᴛᴛɪɴɢꜱ...\n\nɴᴏᴡ ꜱᴇɴᴅ /details ᴀɢᴀɪɴ</b>", reply_markup=reply_markup)
	    
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            await query.answer(script.ALRT_TXT, show_alert=True)
            return
        if set_type == 'is_verify' and query.from_user.id not in ADMINS:
            return await query.answer(text=f"Hey {query.from_user.first_name}, You can't change shortlink settings for your group !\n\nIt's an admin only setting !", show_alert=True)
        if status == "True":
            await save_group_settings(int(grp_id), set_type, False)
            await query.answer("ᴏғғ ❌")
        else:
            await save_group_settings(int(grp_id), set_type, True)
            await query.answer("ᴏɴ ✅")
        settings = await get_settings(int(grp_id))      
        if settings is not None:
            buttons = [[
		InlineKeyboardButton('ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✓' if settings["auto_filter"] else 'ᴏғғ ✗', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}')
            ],[
                InlineKeyboardButton('ꜰɪʟᴇ sᴇᴄᴜʀᴇ', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✓' if settings["file_secure"] else 'ᴏғғ ✗', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}')
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
                InlineKeyboardButton('ᴠᴇʀɪꜰʏ', callback_data=f'setgs#is_verify#{settings["is_verify"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✅' if settings["is_verify"] else 'ᴏғғ ❌', callback_data=f'setgs#is_verify#{settings["is_verify"]}#{grp_id}')
            ],[  
                InlineKeyboardButton('❌ ᴄʟᴏsᴇ ❌', callback_data='close_data')
	    ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            d = await query.message.edit_reply_markup(reply_markup)
            await asyncio.sleep(300)
            await d.delete()
        else:
            await query.message.edit_text("<b>ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ</b>")
            
    elif query.data.startswith("batchfiles"):
        ident, group_id, message_id, user = query.data.split("#")
        group_id = int(group_id)
        message_id = int(message_id)
        user = int(user)
        if user != query.from_user.id:
            await query.answer(script.ALRT_TXT, show_alert=True)
            return
        link = f"https://telegram.me/{temp.U_NAME}?start=allfiles_{group_id}-{message_id}"
        await query.answer(url=link)
        return

async def ai_spell_check(wrong_name):
    async def search_movie(wrong_name):
        search_results = imdb.search_movie(wrong_name)
        movie_list = [movie['title'] for movie in search_results]
        return movie_list
    movie_list = await search_movie(wrong_name)
    if not movie_list:
        return
    for _ in range(5):
        closest_match = process.extractOne(wrong_name, movie_list)
        if not closest_match or closest_match[1] <= 80:
            return 
        movie = closest_match[0]
        files, offset, total_results = await get_search_results(movie)
        if files:
            return movie
        movie_list.remove(movie)
    return

async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        search = message.text
        chat_id = message.chat.id
        settings = await get_settings(chat_id)
       # searching_msg = await msg.reply_text(f'🔎 sᴇᴀʀᴄʜɪɴɢ {search}')
        files, offset, total_results = await get_search_results(search)
      #  await searching_msg.delete()
        if not files:
            if settings["spell_check"]:
                ai_sts = await msg.reply_text(f'𝘼𝙞 𝙨𝙥𝙚𝙡𝙡𝙞𝙣𝙜 𝘾𝙝𝙚𝙘𝙠⚡😎')
                is_misspelled = await ai_spell_check(search)
                if is_misspelled:
              #      await ai_sts.edit(f'<b><i>ʏᴏᴜʀ ꜱᴘᴇʟʟɪɴɢ ɪꜱ ᴡʀᴏɴɢ ɴᴏᴡ ᴅᴇᴠɪʟ ꜱᴇᴀʀᴄʜɪɴɢ ᴡɪᴛʜ ᴄᴏʀʀᴇᴄᴛ ꜱᴘᴇʟʟɪɴɢ - <code>{is_misspelled}</code></i></b>')
                    await asyncio.sleep(2)
                    msg.text = is_misspelled
                    await ai_sts.delete()
                    return await auto_filter(client, msg)
                await ai_sts.delete()
                return await advantage_spell_chok(msg)
            return
    #else:
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    req = message.from_user.id if message.from_user else 0
    key = f"{message.chat.id}-{message.id}"
    batch_ids = files
    ads, ads_name, _ = await mdb.get_advirtisment()
    ads_text = ""
    if ads is not None and ads_name is not None:
        ads_url = f"https://t.me/{temp.U_NAME}?start=ads"
        ads_text = f"<a href={ads_url}>{ads_name}</a>"
    ads = f"\n━━━━━━━━━━━━━━━━━━\n <b>{ads_text}</b> \n━━━━━━━━━━━━━━━━━━" if ads_text else ""
    temp.FILES_ID[f"{message.chat.id}-{message.id}"] = batch_ids
    batch_link = f"batchfiles#{message.chat.id}#{message.id}#{message.from_user.id}"
    pre = 'filep' if settings['file_secure'] else 'file'
    temp.CHAT[message.from_user.id] = message.chat.id
    settings = await get_settings(message.chat.id)
    del_msg = f"\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    links = ""
    if settings["link"]:
        btn = []
        for file_num, file in enumerate(files, start=1):
            links += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{message.chat.id}_{file.file_id}>[{get_size(file.file_size)}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}</a></b>"""
    else:
        btn = [[InlineKeyboardButton(text=f"🔗 {get_size(file.file_size)}≽ {get_name(file.file_name)}", url=f'https://telegram.dog/{temp.U_NAME}?start=file_{message.chat.id}_{file.file_id}'),]
               for file in files
              ]
    if offset != "":
        if total_results >= MAX_BTN:
            btn.insert(0,[
                InlineKeyboardButton("‼️ ʟᴀɴɢᴜᴀɢᴇ ‼️", callback_data=f"languages#{key}#{offset}#{req}"),
                ])
            btn.insert(1, [
                InlineKeyboardButton("◖ ǫᴜᴀʟɪᴛʏ ◗", callback_data=f"qualities#{key}#{offset}#{req}"),
                InlineKeyboardButton("◖ sᴇᴀsᴏɴ ◗", callback_data=f"seasons#{key}#{offset}#{req}"),
            ])
            btn.insert(3,[
		   # InlineKeyboardButton("🥇 ʙᴜʏ", callback_data="seeplans"),
                InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link),
		    InlineKeyboardButton("🥇 ʙᴜʏ", callback_data="seeplans"),
                ])
        else:
            btn.insert(0,[
		  #  InlineKeyboardButton("🥇 ʙᴜʏ", callback_data="seeplans"),
                InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link),
		    InlineKeyboardButton("🥇 ʙᴜʏ", callback_data="seeplans"),
            ])
            btn.insert(1,[
                InlineKeyboardButton("No More Pages", user_id=ADMINS[0])
            ])
    else:
        btn.insert(0,[
	 #   InlineKeyboardButton("🥇 ʙᴜʏ", callback_data="seeplans"),
            InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link),
		InlineKeyboardButton("🥇 ʙᴜʏ", callback_data="seeplans"),
            ])

        btn.insert(1,[
            InlineKeyboardButton("No More Pages", user_id=ADMINS[0])
        ])
	
    if spoll:
        m = await msg.message.edit(f"<b><code>{search}</code> ɪs ꜰᴏᴜɴᴅ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ꜰᴏʀ ꜰɪʟᴇs 📫</b>")
        await asyncio.sleep(1.2)
        await m.delete()

    if offset != "":
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"1/{math.ceil(int(total_results) / int(MAX_BTN))}", callback_data="pages"),
             InlineKeyboardButton(text="ɴᴇxᴛ ⪼", callback_data=f"next_{req}_{key}_{offset}")]
        )
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        try:
            offset = int(offset) 
        except:
            offset = int(MAX_BTN)
        
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"<b>📂 ʜᴇʀᴇ ɪ ꜰᴏᴜɴᴅ ꜰᴏʀ ʏᴏᴜʀ sᴇᴀʀᴄʜ {search}\n\n📢 ʀᴇǫᴜᴇꜱᴛᴇᴅ ʙʏ - {message.from_user.mention}\n♾️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ - {message.chat.title}\n\n<u>🍿 Your Movie Files 👇</u></b>"
	    #= f"<b>🏷 ᴛɪᴛʟᴇ - {title}\n🎭 ɢᴇɴʀᴇꜱ - {genres}\n📆 ʏᴇᴀʀ - {year}\n🌟 ʀᴀᴛɪɴɢ - {rating}\n🔊 ʟᴀɴɢᴜᴀɢᴇ - {languages}\n📀 ʀᴜɴᴛɪᴍᴇ - {runtime}\n📢 ʀᴇǫᴜᴇꜱᴛᴇᴅ ʙʏ - {message.from_user.mention}\n♾️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ - {message.chat.title}</b>"

    ads, ads_name, _ = await mdb.get_advirtisment()
    ads_text = ""
    if ads is not None and ads_name is not None:
        ads_url = f"https://t.me/{temp.U_NAME}?start=ads"
        ads_text = f"<a href={ads_url}>{ads_name}</a>"
    ads = f"\n━━━━━━━━━━━━━━━━━━\n <b>{ads_text}</b> \n━━━━━━━━━━━━━━━━━━" if ads_text else ""
    del_msg = f"\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    CAP[key] = cap
    if imdb and imdb.get('poster'):
        try:
            if settings['auto_delete']:
                k = await message.reply_text(text=cap + links + del_msg + ads, parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btn))
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass
            else:
                await message.reply_text(text=cap + links + del_msg + ads, reply_markup=InlineKeyboardMarkup(btn))                    
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            if settings["auto_delete"]:
                k = await message.reply_text(text=cap + links + del_msg + ads, parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btn))
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass
            else:
                await message.reply_text(text=cap + links + del_msg + ads, parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btn))
        except Exception as e:
            print(e)
            if settings["auto_delete"]:
                k = await message.reply_text(cap + links + del_msg + ads, parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass
            else:
                await message.reply_text(cap + links + del_msg + ads, parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
    else:
        k=await message.reply_text(text=cap + links + del_msg + ads, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btn), reply_to_message_id=message.id)
        if settings['auto_delete']:
            await asyncio.sleep(DELETE_TIME)
            await k.delete()
            try:
                await message.delete()
            except:
                pass
    return            

		    
         #   if NO_SEARCH == True:
           #     await message.reply_text(cap + links + del_msg + ads, parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
      #      else:
           #     k = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024] + links + del_msg, parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btn))

async def advantage_spell_chok(message):
    mv_id = message.id
    search = message.text
    chat_id = message.chat.id
    settings = await get_settings(chat_id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", message.text, flags=re.IGNORECASE)
    RQST = query.strip()
    query = query.strip() + " movie"
    try:
        movies = await get_poster(search, bulk=True)
    except:
        k = await message.reply(script.I_CUDNT.format(message.from_user.mention))
        await asyncio.sleep(60)
        await k.delete()
        try:
            await message.delete()
        except:
            pass
        return
    if not movies:
        google = search.replace(" ", "+")
        button = [[
            InlineKeyboardButton("🔍 ᴄʜᴇᴄᴋ sᴘᴇʟʟɪɴɢ ᴏɴ ɢᴏᴏɢʟᴇ 🔍", url=f"https://www.google.com/search?q={google}")
        ]]
        k = await message.reply_text(text=script.I_CUDNT.format(search), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(120)
        await k.delete()
        try:
            await message.delete()
        except:
            pass
        return
    user = message.from_user.id if message.from_user else 0
    buttons = [[
        InlineKeyboardButton(text=movie.get('title'), callback_data=f"spol#{movie.movieID}#{user}")
    ]
        for movie in movies
    ]
    buttons.append(
        [InlineKeyboardButton(text="🚫 ᴄʟᴏsᴇ 🚫", callback_data='close_data')]
    )
    d = await message.reply_text(text=script.CUDNT_FND.format(message.from_user.mention), reply_markup=InlineKeyboardMarkup(buttons), reply_to_message_id=message.id)
    await asyncio.sleep(120)
    await d.delete()
    try:
        await message.delete()
    except:
        pass
