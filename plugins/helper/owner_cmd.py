import asyncio
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
from info import ADMINS
from pyrogram import Client, filters
from pyrogram.types import BotCommand
from info import ADMINS

@Client.on_message(filters.command("owner_cmd") & filters.user(ADMINS))
async def admin_cmd(client, message):
    # Define the buttons
    buttons = [
        [KeyboardButton("/premium"), KeyboardButton("/premium_user")],
        [KeyboardButton("/add_redeem"), KeyboardButton("/broadcast")],
        [KeyboardButton("/grp_broadcast"), KeyboardButton("/remove_premium")],
        [KeyboardButton("/groups"), KeyboardButton("/leave")],
        [KeyboardButton("/pm_search_off"), KeyboardButton("/pm_search_on")],
        [KeyboardButton("/movie_update_off"), KeyboardButton("/movie_update_on")],
        [KeyboardButton("/send"), KeyboardButton("/stats")],
        [KeyboardButton("/deleteall"), KeyboardButton("/delete")],
        [KeyboardButton("/grp_delete"), KeyboardButton("/check_plan")],
        [KeyboardButton("/del_file"), KeyboardButton("/deletefiles")],
        [KeyboardButton("/del_ads"), KeyboardButton("/set_ads")],
        [KeyboardButton("/search"), KeyboardButton("/channel")],
        [KeyboardButton("/invite"), KeyboardButton("/index")],
        [KeyboardButton("/getfile")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)
    
    # Send the reply message with the admin commands
    k = await message.reply(
        "<b>Admin All Commands 👇\n 2 minutes me delete</b>",
        reply_markup=reply_markup,
    )
    await asyncio.sleep(120)
    await k.delete()
