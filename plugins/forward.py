from pyrogram import Client, emoji, filters
from database import get_search_results, Data
from config import OWNER_ID, TO_CHANNEL, COLLECTION_NAME, DATABASE_NAME
import asyncio
from pyrogram.errors import FloodWait
import random
from pyrogram.errors.exceptions.bad_request_400 import FileReferenceEmpty, FileReferenceExpired, MediaEmpty
import pytz
from datetime import datetime
from pyrogram.enums import ParseMode
#from databse import db
#db = client[DATABASE_NAME]

IST = pytz.timezone('Asia/Kolkata')
MessageCount = 0
BOT_STATUS = "0"
status = set(int(x) for x in (BOT_STATUS).split())
OWNER = int(OWNER_ID)
@Client.on_message(filters.command("status"))
async def count(bot, m):
    if 1 in status:
        await m.reply_text("Currently Bot is forwarding messages.", parse_mode=ParseMode.HTML)  # Use HTML or MARKDOWN
    elif 2 in status:
        await m.reply_text("Now Bot is Sleeping", parse_mode=ParseMode.HTML)
    else:
        await m.reply_text("Bot is Idle now, You can start a task.", parse_mode=ParseMode.HTML)

@Client.on_message(filters.command('totala'))
async def totala(bot, message):
    msg = await message.reply("Counting total messages in DB...", quote=True)
    try:
        # Ensure the Data object is properly checked before using it
        if Data is not None:
            total = await Data.count_documents({})
            await msg.edit(f'Total Messages: {total}')
        else:
            await msg.edit("Error: Database is not initialized.")
    except Exception as e:
        await msg.edit(f'Error: {e}')

@Client.on_message(filters.command('totalb'))
async def totalb(bot, message):
    msg = await message.reply("Counting total messages in DB...", quote=True)
    try:
        # Check if Data is properly initialized
        if Data is not None:
            total = await Data.count_documents({})
            if total:  # If total is not None or greater than 0
                await msg.edit(f'Total Messages: {total}')
            else:
                await msg.edit("No messages found in the database.")
        else:
            await msg.edit("Error: Database is not initialized.")
    except Exception as e:
        await msg.edit(f'Error: {e}')
@Client.on_message(filters.command('total'))
async def totald(bot, message):
    msg = await message.reply("Counting total messages in DB...", quote=True)
    try:
        total = await Data.count_documents()
        await msg.edit(f'Total Messages: {total}')
    except Exception as e:
        await msg.edit(f'Error: {e}')
        


@Client.on_message(filters.command('cleardb'))
async def clrdb(bot, message):
    msg = await message.reply("Clearing files from DB...", quote=True, parse_mode=ParseMode.HTML)
    try:
        await Data.collection.drop()
        await msg.edit(f'Cleared DB', parse_mode=ParseMode.HTML)
    except Exception as e:
        await msg.edit(f'Error: {e}', parse_mode=ParseMode.HTML)

@Client.on_message(filters.command('cleardbf'))
async def c1lrdb(bot, message):
    msg = await message.reply("Clearing files from DB...", quote=True, parse_mode=ParseMode.HTML)
    try:
        # Drop the collection using pymongo's client directly
        db.drop_collection(COLLECTION_NAME)
        await msg.edit(f'Cleared DB', parse_mode=ParseMode.HTML)
    except Exception as e:
        await msg.edit(f'Error: {e}', parse_mode=ParseMode.HTML)

import asyncio
import random
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, FileReferenceExpired, FileReferenceEmpty, MediaEmpty
from datetime import datetime

@Client.on_message(filters.command("forward"))
async def forward(bot, message):
    if 1 in status:
        await message.reply_text("A task is already running.", parse_mode=ParseMode.HTML)
        return
    if 2 in status:
        await message.reply_text("Sleeping the engine to avoid a ban.", parse_mode=ParseMode.HTML)
        return

    m = await bot.send_message(chat_id=OWNER, text="Started Forwarding", parse_mode=ParseMode.HTML)
    global MessageCount
    MessageCount = 0
    mcount, acount, bcount, ccount = [random.randint(x, y) for x, y in [(10000, 15300), (5000, 6000), (1500, 2000), (250, 300)]]

    while await Data.count_documents({}) != 0:
        data = await get_search_results()
        for msg in data:
            channel = msg['channel']
            file_id = msg['id']
            message_id = msg['message_id']
            methord = msg['methord']
            caption = msg['caption']
            file_type = msg['file_type']
            chat_id = TO_CHANNEL

            try:
                if methord == "bot":
                    await handle_forward_as_bot(bot, chat_id, channel, file_id, message_id, caption, file_type)
                elif methord == "user":
                    await handle_forward_as_user(bot, chat_id, channel, file_id, message_id, caption, file_type, mcount, acount, bcount, ccount)
                
                # Delete the processed message from the database
                await Data.collection.delete_one({
                    'channel': channel,
                    'message_id': message_id,
                    'file_type': file_type,
                    'methord': methord,
                    'use': "forward"
                })

                # Update counts and statuses
                MessageCount += 1
                mcount, acount, bcount, ccount = [x - 1 for x in (mcount, acount, bcount, ccount)]
                await update_status_message(bot, m, methord, MessageCount)

            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Error: {e}")
                await bot.send_message(chat_id=OWNER, text=f"LOG-Error: {e}", parse_mode=ParseMode.HTML)

        if ccount <= 0:  # Reset counters to avoid bans
            await sleep_to_avoid_ban(bot, m)

async def handle_forward_as_bot(bot, chat_id, channel, file_id, message_id, caption, file_type):
    try:
        if file_type in ("document", "video", "audio", "photo"):
            await bot.send_cached_media(chat_id=chat_id, file_id=file_id, caption=caption, parse_mode=ParseMode.HTML)
        else:
            await bot.copy_message(chat_id=chat_id, from_chat_id=channel, message_id=message_id, caption=caption)
        await asyncio.sleep(1)
    except (FileReferenceExpired, MediaEmpty):
        fetch = await bot.get_messages(channel, message_id)
        new_file_id = get_new_file_id(fetch, file_type)
        await bot.send_cached_media(chat_id=chat_id, file_id=new_file_id, caption=caption, parse_mode=ParseMode.HTML)

async def handle_forward_as_user(bot, chat_id, channel, file_id, message_id, caption, file_type, *counts):
    try:
        if file_type in ("document", "video", "audio", "photo"):
            await bot.USER.send_cached_media(chat_id=chat_id, file_id=file_id, caption=caption, parse_mode=ParseMode.HTML)
        else:
            await bot.USER.copy_message(chat_id=chat_id, from_chat_id=channel, message_id=message_id, caption=caption)
        await asyncio.sleep(1)
    except (FileReferenceExpired, MediaEmpty):
        fetch = await bot.USER.get_messages(channel, message_id)
        new_file_id = get_new_file_id(fetch, file_type)
        await bot.USER.send_cached_media(chat_id=chat_id, file_id=new_file_id, caption=caption, parse_mode=ParseMode.HTML)

async def update_status_message(bot, m, methord, MessageCount):
    datetime_ist = datetime.now().strftime("%I:%M:%S %p - %d %B %Y")
    await m.edit(
        text=f"Total Forwarded : <code>{MessageCount}</code>\nForwarded Using: {methord.capitalize()}\nLast Forwarded at {datetime_ist}",
        parse_mode=ParseMode.HTML
    )

async def sleep_to_avoid_ban(bot, m):
    csleep = random.randint(250, 500)
    datetime_ist = datetime.now().strftime("%I:%M:%S %p - %d %B %Y")
    await m.edit(
        text=f"You have sent {MessageCount} messages.\nWaiting for {csleep} Seconds.\nLast Forwarded at {datetime_ist}",
        parse_mode=ParseMode.HTML
    )
    status.add(2)
    if 1 in status:  # Check if 1 exists before removing
        status.remove(1)
    await asyncio.sleep(csleep)
    # Reset status after sleeping
    status.add(1)
    status.remove(2)
def get_new_file_id(fetch, file_type):
    media = getattr(fetch, file_type, None)
    if media:
        return media.file_id
    raise ValueError(f"No valid media found for file_type: {file_type}")
