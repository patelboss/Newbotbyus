import pytz
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import FloodWait
from config import OWNER_ID, TO_CHANNEL  # Ensure these variables are defined in config
from bot import Bot  # Import the bot instance correctly
from asyncio.exceptions import TimeoutError
from database import save_data, get_search_results  # Ensure database functions are correct
import logging
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, Message
from pyrogram.enums import MessagesFilter
from pyrogram.errors import InviteHashExpired, UserAlreadyParticipant, PeerIdInvalid
import re

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
    if message.from_user.id != OWNER:
        await message.reply_text("Who the hell are you!!")
        return
    while True:
        try:
            chat = await client.ask(text = "To Index a channel you may send me the channel invite link, so that I can join channel and index the files.\n\nIt should be something like <code>https://t.me/xxxxxx</code> or <code>https://t.me/joinchat/xxxxxx</code>", chat_id = message.from_user.id, filters=filters.text, timeout=30)
            channel=chat.text
        except TimeoutError:
            await client.send_message(message.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /index")
            return
            
        except Exception as e:
            
            await message.reply_texf(f'error {e}')
        

        pattern=".*https://t.me/.*"
        result = re.match(pattern, channel, flags=re.IGNORECASE)
        if result:
            print(channel)
            break
        else:
            await chat.reply_text("Wrong URL")
            continue

    if 'joinchat' in channel:
        global channel_type
        channel_type="private"
        try:
            await client.USER.join_chat(channel)
        except UserAlreadyParticipant:
            pass
        except InviteHashExpired:
            await chat.reply_text("Wrong URL or User Banned in channel.")
            return
        
        except Exception as e:
            await message.reply_texf(f'error {e}')
        while True:
            try:
                id = await client.ask(text = "Since this is a Private channel I need Channel id, Please send me channel ID\n\nIt should be something like <code>-100xxxxxxxxx</code>", chat_id = message.from_user.id, filters=filters.text, timeout=30)
                channel=id.text
            except TimeoutError:
                await client.send_message(message.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /index")
                return
            channel=id.text
            if channel.startswith("-100"):
                global channel_id_
                #channel_id_ = channel
                
                channel_id_=int(channel)
                print(channel_id_.text)
                break
            else:
                await chat.reply_text("Wrong Channel ID")
                continue

            
    else:
        #global channel_type
        channel_type="public"
        channel_id = re.search(r"t.me.(.*)", channel)
        #global channel_id_
        channel_id_=channel_id.group(1)

    while True:
        try:
            SKIP = await client.ask(text = "Send me from where you want to start forwarding\nSend 0 for from beginning.", chat_id = message.from_user.id, filters=filters.text, timeout=30)
            print(SKIP.text)
        except TimeoutError:
            await client.send_message(message.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /index")
            return
        try:
            global skip_no
            skip_no=int(SKIP.text)
            break
        except:
            await SKIP.reply_text("Thats an invalid ID, It should be an integer.")
            continue
    while True:
        try:
            LIMIT = await client.ask(text = "Send me from Upto what extend(LIMIT) do you want to Index\nSend 0 for all messages.", chat_id = message.from_user.id, filters=filters.text, timeout=30)
            print(LIMIT.text)
        except TimeoutError:
            await client.send_message(message.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /index")
            return
        try:
            global limit_no
            limit_no=int(LIMIT.text)
            break
        except:
            await LIMIT.reply_text("Thats an invalid ID, It should be an integer.")
            continue

    buttons=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("All Messages", callback_data="all")
            ],
            [
                InlineKeyboardButton("Document", callback_data="docs"),
                InlineKeyboardButton("Photos", callback_data="photos")
            ],
            [
                InlineKeyboardButton("Videos", callback_data="videos"),
                InlineKeyboardButton("Audios", callback_data="audio")
            ]
        ]
        )
    await client.send_message(
        chat_id=message.from_user.id,
        text=f"Ok,\nNow choose what type of messages you want to forward.",
        reply_markup=buttons
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

    #channel_id_ = int(channel_id_) if channel_id_ and str(channel_id_).isdigit() else 0
    
    FROM = channel_id_

    # Validate skip_no and limit_no
    #skip_no = int(skip_no) if skip_no and str(skip_no).isdigit() else 0
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
