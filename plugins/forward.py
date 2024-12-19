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

@Client.on_message(filters.command("forward"))
async def forward(bot, message):
    if 1 in status:
        await message.reply_text("A task is already running.", parse_mode=ParseMode.HTML)
        return
    if 2 in status:
        await message.reply_text("Sleeping the engine for avoiding ban.", parse_mode=ParseMode.HTML)
        return
    m = await bot.send_message(chat_id=OWNER, text="Started Forwarding", parse_mode=ParseMode.HTML)
    global MessageCount
    mcount = random.randint(10000, 15300)
    acount = random.randint(5000, 6000)
    bcount = random.randint(1500, 2000)
    ccount = random.randint(250, 300)
    while await Data.count_documents() != 0:
        data = await get_search_results()
        for msg in data:
            channel = msg.channel
            file_id = msg.id
            message_id = msg.message_id
            methord = msg.methord
            caption = msg.caption
            file_type = msg.file_type
            chat_id = TO_CHANNEL
            if methord == "bot":
                try:
                    if file_type in ("document", "video", "audio", "photo"):
                        await bot.send_cached_media(
                            chat_id=chat_id,
                            file_id=file_id,
                            caption=caption,
                            parse_mode=ParseMode.HTML
                        )
                    else:
                        await bot.copy_message(
                            chat_id=chat_id,
                            from_chat_id=channel,
                            parse_mode=ParseMode.HTML,
                            caption=caption,
                            message_id=message_id
                        )
                    await asyncio.sleep(1)
                    try:
                        status.add(1)
                    except:
                        pass
                    try:
                        status.remove(2)
                    except:
                        pass
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    if file_type in ("document", "video", "audio", "photo"):
                        await bot.send_cached_media(
                            chat_id=chat_id,
                            file_id=file_id,
                            caption=caption,
                            parse_mode=ParseMode.HTML
                        )
                    else:
                        await bot.copy_message(
                            chat_id=chat_id,
                            from_chat_id=channel,
                            parse_mode=ParseMode.HTML,
                            caption=caption,
                            message_id=message_id
                        )
                    await asyncio.sleep(1)
                except Exception as e:
                    print(e)
                    pass
                await Data.collection.delete_one({
                    'channel': channel,
                    'message_id': message_id,
                    'file_type': file_type,
                    'methord': "bot",
                    'use': "forward"
                })
                MessageCount += 1
                try:
                    datetime_ist = datetime.now(IST)
                    ISTIME = datetime_ist.strftime("%I:%M:%S %p - %d %B %Y")
                    await m.edit(text=f"Total Forwarded : <code>{MessageCount}</code>\nForwarded Using: Bot\nSleeping for {1} Seconds\nLast Forwarded at {ISTIME}", parse_mode=ParseMode.HTML)
                except Exception as e:
                    print(e)
                    await bot.send_message(chat_id=OWNER, text=f"LOG-Error: {e}", parse_mode=ParseMode.HTML)
                    pass
            elif methord == "user":
                channel = int(channel)
                if mcount:
                    if acount:
                        if bcount:
                            if ccount:
                                if file_type in ("document", "video", "audio", "photo"):
                                    try:
                                        await bot.USER.send_cached_media(
                                            chat_id=chat_id,
                                            file_id=file_id,
                                            caption=caption,
                                            parse_mode=ParseMode.HTML
                                        )
                                    except FileReferenceExpired:
                                        try:
                                            fetch = await bot.USER.get_messages(channel, message_id)
                                            print("Fetching file_id")
                                            try:
                                                for file_type in ("document", "video", "audio", "photo"):
                                                    media = getattr(fetch, file_type, None)
                                                    if media is not None:
                                                        file_idn = media.file_id
                                                        break
                                                await bot.USER.send_cached_media(chat_id=chat_id, file_id=file_idn, caption=caption, parse_mode=ParseMode.HTML)
                                            except Exception as e:
                                                print(e)
                                                await bot.send_message(OWNER, f"LOG-Error-{e}", parse_mode=ParseMode.HTML)
                                                pass
                                        except:
                                            await bot.send_message(chat_id=OWNER, text=f"LOG-Error: {e}", parse_mode=ParseMode.HTML)
                                            print(e)
                                            pass
                                    except FileReferenceEmpty:
                                        try:
                                            fetch = await bot.USER.get_messages(channel, message_id)
                                            print("Fetching file_ref")
                                            for file_type in ("document", "video", "audio", "photo"):
                                                media = getattr(fetch, file_type, None)
                                                if media is not None:
                                                    file_idn = media.file_id
                                                    break
                                            try:
                                                await bot.USER.send_cached_media(chat_id=chat_id, file_id=file_idn, caption=caption, parse_mode=ParseMode.HTML)
                                            except Exception as e:
                                                print(e)
                                                await bot.send_message(chat_id=OWNER, text=f"LOG-Error: {e}", parse_mode=ParseMode.HTML)
                                                pass
                                        except:
                                            await bot.send_message(chat_id=OWNER, text=f"LOG-Error: {e}", parse_mode=ParseMode.HTML)
                                            print(e)
                                            pass
                                    except MediaEmpty:
                                        try:
                                            fetch = await bot.USER.get_messages(channel, message_id)
                                            for file_type in ("document", "video", "audio", "photo"):
                                                media = getattr(fetch, file_type, None)
                                                if media is not None:
                                                    file_idn = media.file_id
                                                    break
                                            try:
                                                await bot.USER.send_cached_media(chat_id=chat_id, file_id=file_idn, caption=caption, parse_mode=ParseMode.HTML)
                                            except Exception as e:
                                                print(e)
                                                await bot.send_message(chat_id=OWNER, text=f"LOG-Error: {e}", parse_mode=ParseMode.HTML)
                                                pass
                                        except:
                                            await bot.send_message(chat_id=OWNER, text=f"LOG-Error: {e}", parse_mode=ParseMode.HTML)
                                            print(e)
                                            pass
                                    except Exception as e:
                                        print(e)
                                        await bot.send_message(chat_id=OWNER, text=f"LOG-Error: {e}", parse_mode=ParseMode.HTML)
                                        pass
                                else:
                                    try:
                                        await bot.USER.copy_message(
                                            chat_id=chat_id,
                                            from_chat_id=channel,
                                            parse_mode=ParseMode.HTML,
                                            caption=caption,
                                            message_id=message_id
                                        )
                                    except Exception as e:
                                        await bot.send_message(chat_id=OWNER, text=f"LOG-Error: {e}", parse_mode=ParseMode.HTML)
                                        print(e)
                                        pass

                                await Data.collection.delete_one({
                                    'channel': str(channel),
                                    'message_id': message_id,
                                    'methord': "user",
                                    'use': "forward",
                                    'file_type': file_type
                                })
                                try:
                                    status.add(1)
                                except:
                                    pass
                                try:
                                    status.remove(2)
                                except:
                                    pass

                                mcount -= 1
                                ccount -= 1
                                acount -= 1
                                bcount -= 1
                                MessageCount += 1
                                mainsleep = random.randint(3, 8)
                                try:
                                    datetime_ist = datetime.now(IST)
                                    ISTIME = datetime_ist.strftime("%I:%M:%S %p - %d %B %Y")
                                    await m.edit(text=f"Total Forwarded : <code>{MessageCount}</code>\nForwarded Using: User\nSleeping for {mainsleep} Seconds\nLast Forwarded at {ISTIME}", parse_mode=ParseMode.HTML)
                                except FloodWait as e:
                                    print(e)
                                    await bot.send_message(chat_id=OWNER, text=f"Floodwait of {e} sec", parse_mode=ParseMode.HTML)
                                except Exception as e:
                                    await bot.send_message(OWNER, e, parse_mode=ParseMode.HTML)
                                    print(e)
                                    pass
                                print(f"Sleeping:{mainsleep}")
                                await asyncio.sleep(mainsleep)
                            else:
                                try:
                                    status.add(2)
                                except:
                                    pass
                                try:
                                    status.remove(1)
                                except:
                                    pass
                                csleep = random.randint(250, 500)
                                try:
                                    datetime_ist = datetime.now(IST)
                                    ISTIME = datetime_ist.strftime("%I:%M:%S %p - %d %B %Y")
                                    await m.edit(text=f"You have send {MessageCount} messages.\nWaiting for {csleep} Seconds.\nLast Forwarded at {ISTIME}", parse_mode=ParseMode.HTML)
                                except Exception as e:
                                    await bot.send_message(OWNER, e, parse_mode=ParseMode.HTML)
                                    print(e)
                                    pass

                                await asyncio.sleep(csleep)
                                ccount = random.randint(250, 300)
                                print(f"Starting after {csleep/60} minutes")
                                await m.edit(f"Starting after {csleep}", parse_mode=ParseMode.HTML)
                        else:
                            try:
                                status.add(2)
                            except:
                                pass
                            try:
                                status.remove(1)
                            except:
                                pass
                            bsl=random.randint(1000, 1200)
                            try:
                                datetime_ist = datetime.now(IST)
                                ISTIME = datetime_ist.strftime("%I:%M:%S %p - %d %B %Y")
                                await m.edit(text=f"You have send {MessageCount} messages.\nWaiting for {bsl} seconds.\nLast Forwarded at {ISTIME}", parse_mode=ParseMode.HTML)
                            except Exception as e:
                                await bot.send_message(OWNER, e)
                                print(e)
                                pass
                            await asyncio.sleep(bsl)
                            bcount = random.randint(1500, 2000)
                            print(bcount)
                            print(f"Starting after {bsl}")
                            await m.edit(f"Starting after {bsl}", parse_mode=ParseMode.HTML)
                    else:
                        try:
                            status.add(2)
                        except:
                            pass
                        try:
                            status.remove(1)
                        except:
                            pass
                        asl=random.randint(1500, 2000)
                        try:
                            datetime_ist = datetime.now(IST)
                            ISTIME = datetime_ist.strftime("%I:%M:%S %p - %d %B %Y")
                            await m.edit(text=f"You have send {MessageCount} messages.\nWaiting for {asl} seconds.\nLast Forwarded at {ISTIME}", parse_mode=ParseMode.HTML)
                        except Exception as e:
                            await bot.send_message(OWNER, e, parse_mode=ParseMode.HTML)
                            print(e)
                            pass
                        await asyncio.sleep(asl)
                        acount = random.randint(5000, 6000)
                        print(f"Starting after {asl}")
                        await m.edit(f"Starting after {asl}", parse_mode=ParseMode.HTML)
                else:
                    try:
                        status.add(2)
                    except:
                        pass
                    try:
                        status.remove(1)
                    except:
                        pass
                    msl=random.randint(2000, 3000)
                    try:
                        datetime_ist = datetime.now(IST)
                        ISTIME = datetime_ist.strftime("%I:%M:%S %p - %d %B %Y")
                        await m.edit(text=f"You have send {MessageCount} messages.\nWaiting for {msl} seconds.\nLast Forwarded at {ISTIME}", parse_mode=ParseMode.HTML)
                    except Exception as e:
                        
                        await bot.send_message(OWNER, e, parse_mode=ParseMode.HTML)
                        print(e)
                        pass
                    await asyncio.sleep(msl)
                    mcount = random.randint(10000, 15300)
                    print(f"Starting after {msl}")
                    await m.edit(f"Starting after {msl}", parse_mode=ParseMode.HTML)

    print("Finished")
    try:
        await m.edit(text=f'Succesfully Forwarded {MessageCount} messages', parse_mode=ParseMode.HTML)
    except Exception as e:
        await bot.send_message(OWNER, e, parse_mode=ParseMode.HTML)
        print(e)
        pass
    try:
        status.remove(1)
    except:
        pass
    try:
        status.remove(2)
    except:
        pass
    MessageCount=0                                
