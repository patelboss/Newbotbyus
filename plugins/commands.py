import os
import sys
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode  # Import ParseMode for correct parse mode handling
from config import OWNER_ID, LOGGER
#from session_manager import generate_session  # Import session generation
from utils import listen  # Ensure the custom listen function is imported
from pyrogram.types import Message
# Messages
START_MSG = (
    "Hi {},\nThis is a simple bot to forward all messages from one channel to another.\n\n"
    "⚠️ **Warning:**\nYour account may get banned if you forward too many files "
    "from private channels. Use at your own risk!"
)

HELP_MSG = (
    "Available commands:\n\n"
    "/index - To index a channel\n"
    "/forward - To start forwarding\n"
    "/total - Count total messages in the database\n"
    "/status - Check the current status\n"
    "/help - Show help information\n"
    "/stop - Stop all running processes\n\n"
    "Use `/index` to index messages from a channel to the database.\n\n"
    "After indexing, you can start forwarding by using `/forward`.\n\n"
    "**Note:** You will need the following information to index a channel:\n\n"
    "**Channel Invite Link**: If the channel is private, you need to join it to access "
    "the messages. Do not leave the channel until forwarding is complete.\n\n"
    "**Channel ID**: For private channels, use @ChannelidHEXbot to get the ID.\n\n"
    "**SKIP_NO**: Start forwarding files from a specific message number (use `0` to start from the beginning).\n\n"
    "**Caption**: Provide a custom caption for forwarded files. Use `0` to keep the default captions."
)

# Buttons
buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Help", callback_data="help"),
            InlineKeyboardButton("How Does This Work?", callback_data="abt"),
        ],
        [
            InlineKeyboardButton("Source Code", url="https://github.com/subinps/Forward_2.0"),
            InlineKeyboardButton("Report a Bug", url="https://t.me/subinps"),
        ],
    ]
)

# Command: /start
@Client.on_message(filters.private & filters.command('start'))
async def start(client, message):
    LOGGER(__name__).info(f"User {message.from_user.id} started the bot.")
    await client.send_message(
        chat_id=message.chat.id,
        text=START_MSG.format(message.from_user.first_name),
        reply_markup=buttons,
        parse_mode=ParseMode.HTML  # Use ParseMode.HTML for correct parse mode
    )

# Command: /stop
@Client.on_message(filters.command("stop"))
async def stop_command(client, message):
    try:
        # Check if the sender is the owner by comparing as integers
        if message.from_user.id != OWNER_ID:
            return await message.reply("You are not authorized to use this command.", parse_mode=ParseMode.HTML)
        
        # Log the stopping process
        LOGGER(__name__).info("Stopping all processes as requested by the owner.")
        
        # Send a reply message
        msg = await message.reply("Stopping all processes...", parse_mode=ParseMode.HTML)
        
        # Wait a short time before restarting
        await asyncio.sleep(1)
        
        # Edit the message to indicate the bot is restarting
        await msg.edit("All processes stopped and bot restarted.", parse_mode=ParseMode.HTML)
        
        # Restart the bot using os.execl
        os.execl(sys.executable, sys.executable, *sys.argv)
    
    except Exception as e:
        # Log any errors that occur during the process
        LOGGER(__name__).error(f"Error in stop_command: {e}")
        await message.reply(f"An error occurred: {e}", parse_mode=ParseMode.HTML)
        
# Command: /help
@Client.on_message(filters.private & filters.command('help'))
async def help_command(client, message):
    LOGGER(__name__).info(f"User {message.from_user.id} requested help.")
    await client.send_message(
        chat_id=message.chat.id,
        text=HELP_MSG,
        parse_mode=ParseMode.HTML  # Use ParseMode.HTML for correct parse mode
    )

@Client.on_callback_query(filters.regex(r'^help$'))
async def cb_help(bot, cb):
    await cb.message.edit_text(HELP_MSG)



@Client.on_callback_query(filters.regex(r'^abt$'))   
async def cb_abt(bot, cb):
    await cb.message.edit_text("Talking is cheap, Read Code.",
    reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Source", url="https://github.com/subinps/Forward_2.0"),
            ]
        ]
    )
    )

#from pyrogram import Client, filters
#from config import LOGGER
#from utils import listen  # Import your custom listen function
#from session_manager import generate_session

#@Client.on_message(filters.command("login") & filters.private)
#async def login_handler(client, message):
#    user_id = message.from_user.id
#    await message.reply("Starting the login process. Please follow the instructions.", parse_mode=ParseMode.HTML)

  #  try:
        # Step 1: Request phone number from the user
     #   await client.send_message(user_id, "Please provide your phone number to log in:", parse_mode=ParseMode.HTML)

        # Use the custom listen function instead of ask
   #     phone_message = await listen(client, user_id, timeout=60)  # Listen for phone number
      #  phone_number = phone_message.text.strip()  # Get the phone number from the message

        # Step 2: Pass the phone number to the session generation process
        #await generate_session(user_id, client)

#    except Exception as e:
#        # Handle any errors and send a message to the user
#        await client.send_message(user_id, f"An error occurred during login: {e}", parse_mode=ParseMode.HTML)
#        LOGGER(__name__).error(f"Login command error: {e}")
