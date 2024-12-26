from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import FloodWait, InviteHashExpired, UserAlreadyParticipant
from pyrogram.enums import ParseMode, MessagesFilter, ChatType
from datetime import datetime
import pytz
import re
import logging
from asyncio.exceptions import TimeoutError
from config import OWNER_ID #, TO_CHANNEL  # Ensure these variables are defined in config
from bot import Bot  # Import the bot instance correctly
from dataf import * # save_data, get_search_results, get_all_channels, add_channel, remove_channel  # Ensure database functions are correct
import asyncio
import random


# Handler to forward messages from source channels to target channels
#@Client.on_message(filters.channel)
async def forward_messages(client, message):
    # Get all channel mappings
    channel_mappings = get_all_channels()

    for channel in channel_mappings:
        if message.chat.id == channel["source_id"]:
            try:
                # Forward the message as the user
                await client.USER.copy_message(
                    chat_id=channel["target_id"],
                    from_chat_id=message.chat.id,
                    message_id=message.id
                )
                print(f"Forwarded message from {message.chat.id} to {channel['target_id']}")

                # Add a random delay to mimic human behavior
                wait_time = random.uniform(1, 5)  # Random delay between 1 and 5 seconds
                await asyncio.sleep(wait_time)

            except Exception as e:
                print(f"Failed to forward message: {e}")

import asyncio
import random

async def forward_message(client, message):
    """
    Forward messages from source channels to a bot by its username.

    :param client: The Pyrogram client (e.g., client.USER).
    :param message: The incoming message object.
    """
    # Get all channel mappings
    channel_mappings = get_all_channels()

    for channel in channel_mappings:
        if message.chat.id == channel["source_id"]:
            try:
                # Resolve the bot's username to a chat_id
                bot_chat = await client.get_chat(channel["target_bot_username"])
                
                # Forward the message as the user
                await client.USER.copy_message(
                    chat_id=bot_chat.id,
                    from_chat_id=message.chat.id,
                    message_id=message.id
                )
                print(f"Forwarded message from {message.chat.id} to bot {channel['target_bot_username']}")

                # Add a random delay to mimic human behavior
                wait_time = random.uniform(1, 5)  # Random delay between 1 and 5 seconds
                await asyncio.sleep(wait_time)

            except FloodWait as e:
                await asyncio.sleep(e.value)
                print(f"flood wait accure waiting {e.value} second")
            except Exception as e:
                print(f"Failed to forward message: {e}")

from pyrogram import Client, filters
import asyncio
import random

# Your Pyrogram client (assuming user account)
#app = Client("my_account")

# Channel mappings

# Forwarding function
async def forward_messages1(client, message):
    channel_mappings = get_all_channels()

    for channel in channel_mappings:
        if message.chat.id == channel["source_id"]:
            try:
                if "target_bot_username" in channel:
                    # Resolve bot username
                    target_chat = await client.get_chat(channel["target_bot_username"])
                    target_id = target_chat.id
                    print(f"Forwarding to bot: {channel['target_bot_username']}")
                elif "target_id" in channel:
                    # Forward to target channel
                    target_id = channel["target_id"]
                    print(f"Forwarding to channel: {channel['target_id']}")
                else:
                    print("No valid target found in the mapping.")
                    continue

                # Forward message
                await client.copy_message(
                    chat_id=target_id,
                    from_chat_id=message.chat.id,
                    message_id=message.id
                )
                print(f"Forwarded message from {message.chat.id} to {target_id}")

                # Add random delay
                wait_time = random.uniform(2, 9)
                await asyncio.sleep(wait_time)

            except FloodWait as e:
                await asyncio.sleep(e.value)
                print(f"flood wait accure waiting {e.value} second")
            except Exception as e:
                print(f"Failed to forward message: {e}")

# Message handler for source channels
@Client.on_message(filters.chat([channel["source_id"] for channel in get_all_channels()]))
async def handle_message(client, message):
    """
    Trigger the forward_messages function when a message arrives in the source channels.
    """
    await forward_messages1(client, message)

# Run the client
#app.run()

# Command to add a new channel mapping
@Client.on_message(filters.command("addchannel") & filters.user(OWNER_ID))
async def add_channel_command(client, message):
    try:
        # Format: /addchannel source_id target_id
        args = message.text.split()
        if len(args) != 3:
            await message.reply("Usage: /addchannel <source_id> <target_id>")
            return

        source_id = int(args[1])
        target_id = int(args[2])
        add_channel(source_id, target_id)
        await message.reply(f"Added forwarding from {source_id} to {target_id}.")
    except ValueError:
        await message.reply("Error: source_id and target_id must be integers.")
    except Exception as e:
        await message.reply(f"Error: {e}")

# Command to remove an existing channel mapping
@Client.on_message(filters.command("removechannel") & filters.user(OWNER_ID))
async def remove_channel_command(client, message):
    try:
        # Format: /removechannel source_id
        args = message.text.split()
        if len(args) != 2:
            await message.reply("Usage: /removechannel <source_id>")
            return

        source_id = int(args[1])
        remove_channel(source_id)
        await message.reply(f"Removed channel {source_id} from forwarding.")
    except ValueError:
        await message.reply("Error: source_id must be an integer.")
    except Exception as e:
        await message.reply(f"Error: {e}")
