import logging
from database.users_chats_db import db
from pyrogram.errors import UserNotParticipant
import asyncio
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import enums

logger = logging.getLogger(__name__)

async def is_user_fsub(bot, message):
    """
    Check if the user is subscribed to a forced subscription channel.
    This function always returns True, disabling group fsub enforcement.
    PM fsub is handled in commands.py.
    """
    return True
