import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from database import save_string_session  # Custom function to save session
from config import LOGGER

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_session(user_id, client):
    try:
        # Step 1: Request API_ID and API_HASH
        await client.send_message(user_id, "Please send your `API_ID`.")
        api_id_msg = await client.ask(user_id, 'Please send your `API_ID`', filters.text)
        api_id = int(api_id_msg.text.strip())
        await asyncio.sleep(1)
        logger.info(f"Received API_ID: {api_id}")

        await client.send_message(user_id, "Please send your `API_HASH`.")
        api_hash_msg = await client.ask(user_id, 'Please send your `API_Hash`', filters.text)
        api_hash = api_hash_msg.text.strip()
        await asyncio.sleep(1)
        logger.info(f"Received API_HASH: {api_hash}")

        # Step 2: Request phone number
        await client.send_message(user_id, "Please send your phone number (e.g., `+1234567890`).")
        phone_msg = await client.ask(user_id, 'Please send your `Number`', filters.text)
        phone_number = phone_msg.text.strip()
        await asyncio.sleep(1)
        logger.info(f"Received phone number: {phone_number}")

        # Step 3: Initialize Pyrogram client session
        session = Client(name=f"user_{user_id}", api_id=api_id, api_hash=api_hash, in_memory=True)

        await session.connect()
        logger.info("Pyrogram session initialized and connected.")

        # Step 4: Request OTP
        try:
            code = await session.send_code(phone_number)
            logger.info(f"OTP sent to {phone_number}.")
        except (ApiIdInvalid, PhoneNumberInvalid) as e:
            logger.error(f"Error with API credentials or phone number: {e}")
            await client.send_message(user_id, "Invalid API credentials or phone number. Please try again.\nError: {e}" )
            return

        # Request OTP from user
        await client.send_message(user_id, "Check your phone for the OTP and send it here (e.g., `1 2 3 4 5`).")
        otp_msg = await client.ask(user_id, 'Please send your `OTP`', filters.text)
        otp = otp_msg.text.strip()
        logger.info(f"Received OTP: {otp}")

        # Validate OTP format (ensure it's digits with spaces between them)
        if not all(char.isdigit() or char == ' ' for char in otp) or len(otp.split()) < 5:
            logger.warning(f"Invalid OTP format received: {otp}")
            await client.send_message(user_id, "Invalid OTP format. Please make sure the OTP contains only digits with spaces between them (e.g., `1 2 3 4 5`).", parse_mode=ParseMode.HTML)
            return  # Abort the process

        # Step 5: Sign in with OTP
        try:
            await session.sign_in(phone_number, code.phone_code_hash, otp)
            logger.info(f"Successfully signed in with OTP for {phone_number}.")
        except PhoneCodeInvalid:
            logger.error(f"Invalid OTP for {phone_number}.")
            await client.send_message(user_id, "Invalid OTP. Please try again.")
            return
        except PhoneCodeExpired:
            logger.error(f"OTP expired for {phone_number}.")
            await client.send_message(user_id, "OTP expired. Please restart the process.")
            return
        except SessionPasswordNeeded:
            logger.info(f"Two-step verification required for {phone_number}.")
            await client.send_message(user_id, "Two-step verification is enabled. Please send your password.")
            password_msg = await client.ask(user_id, 'Please send your 2fa pass', filters.text)
            password = password_msg.text.strip()

            try:
                await session.check_password(password)
                logger.info(f"Successfully authenticated with 2fa for {phone_number}.")
            except PasswordHashInvalid:
                logger.error(f"Incorrect password for {phone_number}.")
                await client.send_message(user_id, "Incorrect password. Please restart the process.")
                return

        # Step 6: Export session string and save it
        session_string = await session.export_session_string()
        logger.info(f"Generated session string for {phone_number}.")
        save_string_session(session_string, phone_number)
        logger.info(f"Session string saved for {phone_number}.")

        # Notify user of successful session generation
        await client.send_message(
            user_id,
            f"**Session generated successfully!**\n\n`{session_string}`\n\nKeep it secure!",
            parse_mode=ParseMode.MARKDOWN,
        )

        # Send session string to "Saved Messages"
        await session.send_message("me", f"Your session string:\n\n`{session_string}`\n\nKeep it secure.")
        logger.info(f"Session string sent to 'Saved Messages' for {phone_number}.")

        # Disconnect session
        await session.disconnect()
        logger.info(f"Session disconnected for {phone_number}.")
        await asyncio.sleep(30)

        # Restart logic (optional, only if you want to restart the bot)
        #await client.stop()
        #await client.start()
        

    except Exception as e:
        logger.error(f"Error during session generation for {user_id}: {e}")
        await client.send_message(user_id, "An error occurred during session generation. Please try again.")
