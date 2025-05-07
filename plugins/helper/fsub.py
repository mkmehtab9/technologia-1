from pyrogram import Client, filters, enums
from database.users_chats_db import db
from info import ADMINS, AUTH_CHANNEL, LOG_CHANNEL
from utils import get_settings, save_group_settings, is_check_admin
import logging

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("fsub"))
async def force_subscribe(client, message):
    m = await message.reply_text("Wait im checking...")
    if message.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await m.edit("This command is only for groups!")
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await m.edit("Only group admins can use this command!")
    try:
        toFsub = message.command[1]
    except IndexError:
        return await m.edit("Usage: /fsub CHAT_ID")
    if not toFsub.startswith("-100"):
        toFsub = "-100" + toFsub
    if not toFsub[1:].isdigit() or len(toFsub) != 14:
        return await m.edit("CHAT_ID isn't valid!")
    toFsub = int(toFsub)
    if toFsub == message.chat.id:
        return await m.edit("It seems like you're attempting to enable force subscription for this chat ID. Please use a different chat ID!")
    if not await is_check_admin(client, toFsub, client.me.id):
        return await m.edit("I need to be an admin in the given chat to perform this action!\nMake me admin in your Target chat and try again.")
    try:
        grp_id = message.chat.id
        await save_group_settings(grp_id, {'fsub': toFsub})
        settings = await get_settings(grp_id)
        saved_fsub = settings.get('fsub')
        if saved_fsub != toFsub:
            raise Exception(f"Failed to save fsub. Expected {toFsub}, got {saved_fsub}")
        await m.edit(f"Successfully added force subscribe to {toFsub} in {message.chat.title}")
        try:
            await client.send_message(
                LOG_CHANNEL,
                f"#Fsub_Channel_set\n\nUser - {message.from_user.mention} set the force channel for:\n\nFsub channel - {message.chat.title}\nChat ID - {toFsub}"
            )
        except Exception as log_e:
            logger.error(f"Failed to send log message: {log_e}")
    except Exception as e:
        logger.error(f"Error setting fsub for group {message.chat.id}: {e}")
        await m.edit(f"Something went wrong! Error: {e}\nTry again later or report in Support Group @AV_SUPPORT_GROUP")

@Client.on_message(filters.command("del_fsub"))
async def del_force_subscribe(client, message):
    m = await message.reply_text("Wait im checking...")
    if message.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await m.edit("This command is only for groups!")
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await m.edit("Only group admins can use this command!")
    try:
        grp_id = message.chat.id
        settings = await get_settings(grp_id)
        if 'fsub' not in settings or settings['fsub'] is None:
            await m.edit(f"Force subscribe not found in {message.chat.title}")
            return
        await save_group_settings(grp_id, {'fsub': None})
        await m.edit(f"Successfully removed force subscribe for - {message.chat.title}\nTo add again use <code>/fsub YOUR_FSUB_CHAT_ID</code>")
    except Exception as e:
        logger.error(f"Error deleting fsub for group {message.chat.id}: {e}")
        await m.edit("Error removing fsub! Try again later.")

@Client.on_message(filters.command("show_fsub") & filters.group)
async def show_fsub(client, message):
    m = await message.reply_text("Wait im checking...")
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await m.edit("Only group admins can use this command!")
    try:
        grp_id = message.chat.id
        settings = await get_settings(grp_id)
        fsub = settings.get('fsub')
        if fsub:
            invite_link = await client.export_chat_invite_link(fsub)
            await m.edit(f"Force subscribe is set to {fsub}\n<a href={invite_link}>Channel Link</a>", disable_web_page_preview=True)
        else:
            await m.edit(f"Force subscribe is not set in {message.chat.title}\nDefault AUTH_CHANNEL: {AUTH_CHANNEL}")
    except Exception as e:
        logger.error(f"Error showing fsub for group {message.chat.id}: {e}")
        await m.edit("Error fetching fsub! Try again later.")
