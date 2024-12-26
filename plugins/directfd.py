from pyrogram import Client, filters
from dataf import *
import pytz
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import InviteHashExpired, UserAlreadyParticipant
from config import OWNER_ID, TO_CHANNEL  # Ensure these variables are defined in config
import re
from bot import Bot  # Import the bot instance correctly
from asyncio.exceptions import TimeoutError
from database import save_data, get_search_results  # Ensure database functions are correct
import logging
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, Message
from pyrogram.enums import MessagesFilter
from pyrogram import enums

@Client.on_message(filters.Channel)
async def forward_messages(client, message):
    # Get all channel mappings
    channel_mappings = get_all_channels()

    for channel in channel_mappings:
        if message.chat.id == channel["source_id"]:
            try:
                # Forward the message to the target channel
                await client.USER.forward_messages(
                    chat_id=channel["target_id"],
                    from_chat_id=message.chat.id,
                    message_ids=message.id
                )
                print(f"Forwarded message from {message.chat.id} to {channel['target_id']}")
            except Exception as e:
                print(f"Failed to forward message: {e}")

@Client.on_message(filters.command("addchannel"))
async def add_channel_command(client, message):
    try:
        # Format: /addchannel source_id target_id
        args = message.text.split()
        source_id = int(args[1])
        target_id = int(args[2])
        add_channel(source_id, target_id)
        await message.reply(f"Added forwarding from {source_id} to {target_id}.")
    except Exception as e:
        await message.reply(f"Error: {e}")

@Client.on_message(filters.command("removechannel"))
async def remove_channel_command(client, message):
    try:
        # Format: /removechannel source_id
        args = message.text.split()
        source_id = int(args[1])
        remove_channel(source_id)
        await message.reply(f"Removed channel {source_id} from forwarding.")
    except Exception as e:
        await message.reply(f"Error: {e}")
