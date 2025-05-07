from datetime import timedelta, datetime
import pytz
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS, PREMIUM_LOGS
from utils import get_seconds
from database.users_chats_db import db
import string
import random

VALID_REDEEM_CODES = {}

def generate_code(length=8):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=14))

@Client.on_message(filters.command("add_redeem") & filters.user(ADMINS))
async def add_redeem_code(client, message):
    user_id = message.from_user.id
    if len(message.command) == 3:
        try:
            time = message.command[1]
            num_codes = int(message.command[2])
        except ValueError:
            await message.reply_text("Please provide a valid number of codes to generate.")
            return

        codes = []
        for _ in range(num_codes):
            code = generate_code()
            VALID_REDEEM_CODES[code] = time
            codes.append(code)

        codes_text = '\n'.join(f"➔ <code>/redeem {code}</code>" for code in codes)
        response_text = f"""
<b>Gɪғᴛᴄᴏᴅᴇ Gᴇɴᴇʀᴀᴛᴇᴅ ✅
Aᴍᴏᴜɴᴛ:</b> {num_codes}

{codes_text}
<b>Duration:</b> {time}

🔰<u>𝗥𝗲𝗱𝗲𝗲𝗺 𝗜𝗻𝘀𝘁𝗿𝘂𝗰𝘁𝗶𝗼𝗻</u>🔰
<b>𝙹𝚄𝚂𝚃 𝙲𝙻𝙸𝙲𝙺 𝚃𝙷𝙴 𝙰𝙱𝙾𝚅𝙴 𝙲𝙾𝙳𝙴 𝚃𝙾 𝙲𝙾𝙿𝚈 𝙰𝙽𝙳 𝚃𝙷𝙴𝙽 𝚂𝙴𝙽𝙳 𝚃𝙷𝙰𝚃 𝙲𝙾𝙳𝙴 𝚃𝙾 𝚃𝙷𝙴 𝙱𝙾𝚃, 𝚃𝙷𝙰𝚃'𝚂 𝙸𝚃 💖</b>"""

        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("♻️ ʀᴇᴅᴇᴇᴍ ʜᴇʀᴇ ♻️", url="http://t.me/aimoviefilterbot")],
                [InlineKeyboardButton("❕ ᴀɴʏ ǫᴜᴇʀʏ ❕", url="https://t.me/Dg_shiva")]
            ]
        )

        await message.reply_text(response_text, reply_markup=keyboard)
    else:
        await message.reply_text("<b>♻ Usage:\n\n➩ <code>/add_redeem 1day 5</code>,\n➩ <code>/add_redeem 7day 5</code>,\n➩ <code>/add_redeem 30day 5</code>,\n➩ <code>/add_redeem 60day 5</code>,\n➩ <code>/add_redeem 90day 5</code>,</b>")


@Client.on_message(filters.command("redeem"))
async def redeem_code(client, message):
    user_id = message.from_user.id
    if len(message.command) == 2:
        redeem_code = message.command[1]

        if redeem_code in VALID_REDEEM_CODES:
            try:
                time = VALID_REDEEM_CODES.pop(redeem_code)
                user = await client.get_users(user_id)

                try:
                    seconds = await get_seconds(time)
                except Exception as e:
                    await message.reply_text("Invalid time format in redeem code.")
                    return

                if seconds > 0:
                    data = await db.get_user(user_id)
                    current_expiry = data.get("expiry_time") if data else None

                    now_aware = datetime.now(pytz.utc)

                    if current_expiry:
                        current_expiry = current_expiry.replace(tzinfo=pytz.utc)

                    if current_expiry and current_expiry > now_aware:
                        expiry_str_in_ist = current_expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ Expiry Time: %I:%M:%S %p")
                        await message.reply_text(
                            f"#𝐀𝐥𝐫𝐞𝐚𝐝𝐲_𝐏𝐫𝐞𝐦𝐢𝐮𝐦 ❌\n\nʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ\n\nʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴜsᴇ ᴛʜɪs ᴄᴏᴅᴇ",
                            disable_web_page_preview=True
                        )
                        return

                    expiry_time = now_aware + timedelta(seconds=seconds)
                    user_data = {"id": user_id, "expiry_time": expiry_time}
                    await db.update_user(user_data)

                    expiry_str_in_ist = expiry_time.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ Expiry Time: %I:%M:%S %p")

                    await message.reply_text(f"ʜᴀʏ {user.mention} ʏᴏᴜʀ 🎉 ᴄᴏᴅᴇ ʀᴇᴅᴇᴇᴍᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ! ɴᴏᴡ ʜᴀᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ᴜɴᴛɪʟ ᴠɪᴇᴡ ᴘʟᴀɴ ᴅᴇᴛᴀɪʟs /myplan\n\n⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : {time}", disable_web_page_preview=True)


                    await client.send_message(
                        PREMIUM_LOGS,
                        text=f"#Redeem_Premium\n\n👤 User: {user.mention}\n⚡ User ID: <code>{user_id}</code>\n⏰ Premium Access: <code>{time}</code>\n⌛️ Expiry Date: {expiry_str_in_ist}",
                        disable_web_page_preview=True
                    )
                else:
                    await message.reply_text("Invalid time format in redeem code.")
            except Exception as e:
                await message.reply_text(f"An error occurred while redeeming the code: {e}")
        else:
            await message.reply_text("Invalid Redeem Code or Expired.")
    else:
        await message.reply_text("Usage: /redeem <code>")
        
