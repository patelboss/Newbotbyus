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
from user import User

from pyrogram import Client, filters
from config import OWNER_ID  # Ensure OWNER_ID is defined in config
 #from user import USER  # Import the user client instance
from dataf import get_all_channels, add_channel, remove_channel  # Ensure these are properly implemented
import asyncio
import random
from pyrogram.errors import FloodWait

USER: User = None
USER_ID: int = None
await super().start()
self.USER, self.USER_ID = await User().start()
# Forwarding function
@USER.on_message(filters.create(lambda _, __, message: message.chat.id in [ch["source_id"] for ch in get_all_channels()]))
async def handle_message(client, message):
    """
    Handles incoming messages dynamically by verifying the source channel.
    """
    # Log the incoming message for debugging
    print(f" Bot User Received message from source channel {message.chat.id}: {message.text}")

    # Forward the message using the user account
    await forward_messages1(client, message)

async def forward_messages1(client, message):
    """
    Forwards a message from source channels to their mapped target channels.
    """
    channel_mappings = get_all_channels()

    for channel in channel_mappings:
        if message.chat.id == channel["source_id"]:
            try:
                target_id = None

                if "target_bot_username" in channel:
                    # Resolve bot username to get the target chat ID
                    target_chat = await client.get_chat(channel["target_bot_username"])
                    target_id = target_chat.id
                elif "target_id" in channel:
                    # Directly use the target channel ID
                    target_id = channel["target_id"]

                if target_id:
                    await USER.copy_message(
                        chat_id=target_id,
                        from_chat_id=message.chat.id,
                        message_id=message.id
                    )
                    print(f"Forwarded message from {message.chat.id} to {target_id}")

                    # Add random delay to avoid rate limits
                    wait_time = random.uniform(2, 9)
                    await asyncio.sleep(wait_time)

            except FloodWait as e:
                print(f"Flood wait triggered, waiting {e.value} seconds...")
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Failed to forward message: {e}")

             
# Dynamic message handler
#@User.on_message(filters.create(lambda _, __, message: message.chat.id in [ch["source_id"] for ch in get_all_channels()]))
#async def handle_message(client, message):
 
    """
    Handles incoming messages dynamically by checking if the source channel is in the database.
    """
  #  print(f"User vala Received message from source channel {message.chat.id}: {message.text}")
   # await forward_messages1(client, message)
#@Bot.USER.on_message(filters.create(lambda _, __, message: message.chat.id in [ch["source_id"] for ch in get_all_channels()]))
#async def handle_message(client, message):
    """
    Handles incoming messages dynamically by verifying the source channel.
    """
    # Log the incoming message for debugging
    #print(f" Bot User Received message from source channel {message.chat.id}: {message.text}")

    # Forward the message using the user account
    #await forward_messages1(client, message)
# Command to add a new channel mapping
@Client.on_message(filters.command("addchannel") & filters.user(OWNER_ID))
async def add_channel_command(client, message):
    """
    Adds a new channel mapping to the database.
    Usage: /addchannel <source_id> <target_id>
    """
    try:
        args = message.text.split()
        if len(args) != 3:
            await message.reply("Usage: /addchannel <source_id> <target_id>")
            return

        source_id = int(args[1])
        target_id = int(args[2])
        add_channel(source_id, target_id)  # Save the mapping in the database
        await message.reply(f"Added forwarding from {source_id} to {target_id}.")
    except ValueError:
        await message.reply("Error: source_id and target_id must be integers.")
    except Exception as e:
        await message.reply(f"Error: {e}")

# Command to remove an existing channel mapping
@Client.on_message(filters.command("removechannel") & filters.user(OWNER_ID))
async def remove_channel_command(client, message):
    """
    Removes an existing channel mapping from the database.
    Usage: /removechannel <source_id>
    """
    try:
        args = message.text.split()
        if len(args) != 2:
            await message.reply("Usage: /removechannel <source_id>")
            return

        source_id = int(args[1])
        remove_channel(source_id)  # Remove the mapping from the database
        await message.reply(f"Removed channel {source_id} from forwarding.")
    except ValueError:
        await message.reply("Error: source_id must be an integer.")
    except Exception as e:
        await message.reply(f"Error: {e}")
