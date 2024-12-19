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
# Logging setup
logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants and Global Variables
IST = pytz.timezone('Asia/Kolkata')
OWNER = int(OWNER_ID)  # Ensuring OWNER is an integer
limit_no = ""
skip_no = ""
caption = ""
channel_type = ""
channel_id_ = ""

# Command: /index
@Client.on_message(filters.private & filters.command(["index"]))
async def run(client: Client, message):
    logger.info(f"User {message.from_user.id} initiated the /index command.")
    
    if message.from_user.id != OWNER:
        await message.reply_text("Who the hell are you!!", parse_mode=ParseMode.HTML)
        logger.warning(f"Unauthorized access attempt by {message.from_user.id}.")
        return

    # Step 1: Ask for the channel link
    while True:
        try:
            chat = await client.ask(
                chat_id=message.from_user.id,
                text="To index a channel, send me the channel invite link.",
                timeout=30,
                parse_mode=ParseMode.HTML
            )
            channel = chat.text.strip()
            if re.match(r".*https://t.me/.*", channel, flags=re.IGNORECASE):
                break
            else:
                await chat.reply_text("Wrong URL, please send a valid invite link.", parse_mode=ParseMode.HTML)
        except TimeoutError:
            await client.send_message(
                message.from_user.id,
                "Error!!\n\nRequest timed out.\nRestart by using /index",
                parse_mode=ParseMode.HTML
            )
            return

    # Step 2: Handle channel type (private/public)
    global channel_type, channel_id_
    if 'joinchat' in channel:
        channel_type = "private"
        try:
            await client.join_chat(channel)
        except UserAlreadyParticipant:
            logger.info("Already a participant in the channel.")
        except InviteHashExpired:
            await message.reply_text("Invalid or expired invite link.", parse_mode=ParseMode.HTML)
            return

        # Ask for Channel ID
        while True:
            try:
                id_chat = await client.ask(
                    chat_id=message.from_user.id,
                    text="Since this is a Private channel, send me the Channel ID.",
                    timeout=30,
                    parse_mode=ParseMode.HTML
                )
                channel_id_ = id_chat.text.strip()
                if channel_id_.startswith("-100"):
                    channel_id_ = int(channel_id_)
                    break
                else:
                    await id_chat.reply_text("Invalid Channel ID. It should start with '-100'.", parse_mode=ParseMode.HTML)
            except TimeoutError:
                await client.send_message(
                    message.from_user.id,
                    "Error!!\n\nRequest timed out.\nRestart by using /index",
                    parse_mode=ParseMode.HTML
                )
                return
    else:
        channel_type = "public"
        match = re.search(r"t.me/(.*)", channel)
        if match:
            channel_id_ = match.group(1)

    # Step 3: Ask for skip and limit values
    while True:
        try:
            skip_chat = await client.ask(
                chat_id=message.from_user.id,
                text="Send me the start point (0 for beginning):",
                timeout=30,
                parse_mode=ParseMode.HTML
            )
            skip_no = int(skip_chat.text.strip())
            break
        except (TimeoutError, ValueError):
            await client.send_message(
                message.from_user.id,
                "Invalid input. Please send a valid number for skip.",
                parse_mode=ParseMode.HTML
            )

    while True:
        try:
            limit_chat = await client.ask(
                chat_id=message.from_user.id,
                text="Send me the limit (0 for all messages):",
                timeout=30,
                parse_mode=ParseMode.HTML
            )
            limit_no = int(limit_chat.text.strip())
            break
        except (TimeoutError, ValueError):
            await client.send_message(
                message.from_user.id,
                "Invalid input. Please send a valid number for limit.",
                parse_mode=ParseMode.HTML
            )

    # Step 4: Message Type Filtering
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("All Messages", callback_data="all")],
            [InlineKeyboardButton("Document", callback_data="docs"),
             InlineKeyboardButton("Photos", callback_data="photos")],
            [InlineKeyboardButton("Videos", callback_data="videos"),
             InlineKeyboardButton("Audios", callback_data="audio")]
        ]
    )
    await client.send_message(
        chat_id=message.from_user.id,
        text="Choose the type of messages to forward.",
        reply_markup=buttons,
        parse_mode=ParseMode.HTML
    )



@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    global skip_no, limit_no  # Ensure these are accessible

    logger.info(f"Callback query received from user {query.from_user.id}. Data: {query.data}")

    # Determine the filter type
    filter = None
    if query.data == "docs":
        filter = MessagesFilter.DOCUMENT
    elif query.data == "all":
        filter = MessagesFilter.EMPTY
    elif query.data == "photos":
        filter = MessagesFilter.PHOTO
    elif query.data == "videos":
        filter = MessagesFilter.VIDEO
    elif query.data == "audio":
        filter = MessagesFilter.AUDIO

    logger.info(f"Filter set to: {filter}")
    caption = None

    # Delete the original message
    await query.message.delete()

    # Ask for a custom caption
    try:
        get_caption = await client.ask(
            chat_id=query.from_user.id,
            text=f"Do you need a custom caption?\n\nIf yes, send me the caption.\n\nIf no, send '0'.",
            parse_mode=ParseMode.HTML,
            timeout=30
            
        )
        input = get_caption.text
        caption = None if input == "0" else input
        logger.info(f"Caption set to: {caption}")
    except TimeoutError:
        logger.error(f"Timeout error while waiting for caption input from user {query.from_user.id}.")
        await client.send_message(
            chat_id=query.from_user.id,
            text="Error!!\n\nRequest timed out.\nRestart by using /index"
        )
        return

    # Notify user that indexing has started
    m = await client.send_message(
        chat_id=query.from_user.id,
        text="Indexing Started"
    )
    logger.info(f"Indexing process initiated for user {query.from_user.id}.")

    # Initialize counters and parameters
    msg_count = 0
    mcount = 0
    FROM = channel_id_

    # Validate skip_no and limit_no
    skip_no = int(skip_no) if skip_no and str(skip_no).isdigit() else 0
    limit_no = int(limit_no) if limit_no and str(limit_no).isdigit() else 100

    try:
        # Iterate through messages in the channel
        async for msg in client.USER.search_messages(chat_id=FROM, offset=skip_no, limit=limit_no, filter=filter):
            logger.debug(f"Processing message ID: {msg.id}")

            channel_type = "public"  # or "private", based on your configuration
            methord = "bot" if channel_type == "public" else "user"
            channel = FROM if channel_type == "public" else str(FROM)

            # Prepare the caption
            msg_caption = caption if caption else (msg.caption or "")
            logger.debug(f"Message caption: {msg_caption}")

            # Determine file type and ID
            file_type = "others"
            id = f"{FROM}_{msg.id}"
            for f_type in ("document", "video", "audio", "photo"):
                media = getattr(msg, f_type, None)
                if media:
                    id = media.file_id
                    file_type = f_type
                    break

            # Save data to the database
            try:
                await save_data(id, channel, msg.id, methord, msg_caption, file_type)
                logger.info(f"Data saved for message ID: {msg.id}")
            except Exception as e:
                logger.error(f"Error saving data for message ID {msg.id}: {e}")
                await client.send_message(OWNER, f"LOG-Error-{e}")
                continue

            # Update counters
            msg_count += 1
            mcount += 1
            new_skip_no = str(skip_no + msg_count)
            logger.debug(f"Total indexed: {msg_count}, Current SKIP_NO: {new_skip_no}")

            # Update progress message every 100 messages
            if mcount == 100:
                try:
                    datetime_ist = datetime.now(IST)
                    ISTIME = datetime_ist.strftime("%I:%M:%S %p - %d %B %Y")
                    await m.edit(
                        text=f"Total Indexed: <code>{msg_count}</code>\nCurrent skip_no: <code>{new_skip_no}</code>\nLast edited at {ISTIME}"
                    )
                    logger.info(f"Progress updated: Total indexed {msg_count}, Current SKIP_NO: {new_skip_no}")
                    mcount = 0
                except FloodWait as e:
                    logger.warning(f"FloodWait encountered: {e.x} seconds.")
                    await asyncio.sleep(e.x)

        # Notify user upon completion
        await m.edit(f"Successfully Indexed <code>{msg_count}</code> messages.")
        logger.info(f"Indexing completed successfully for user {query.from_user.id}. Total messages indexed: {msg_count}.")
    except Exception as e:
        logger.error(f"Error during indexing: {e}")
        await m.edit(text=f"Error: {e}")
