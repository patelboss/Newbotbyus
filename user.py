from config import *
from pyrogram import Client
from udatabase import *

class User(Client):
    def __init__(self):
        # Get the string session synchronously from the database
        session1 = get_string_session()

        # Ensure that a session was found, otherwise raise an error
        if not session1:
            raise ValueError("No session found in the database")

        # Pass the session string directly to the Pyrogram client, bypassing session file name
        super().__init__(
            BOT_USERNAME,
            session_string=SESSION,  # Pass the session string directly to avoid session name length issue
            api_hash=API_HASH,
            api_id=API_ID,
            workers=10
        )
        self.LOGGER = LOGGER

    async def start(self):
        '''Start the user session and perform initial actions.'''
        self.LOGGER(__name__).info("Starting the user session...")
        try:
            # Start the client
            await super().start()
            self.LOGGER(__name__).info("Session successfully verified.")
            
            if BOT_USERNAME:
                self.LOGGER(__name__).info(f"Sending a command to bot @{BOT_USERNAME}.")
                # Send a message to the bot
                await self.send_message(chat_id=BOT_USERNAME, text="/forward")
                self.LOGGER(__name__).info(f"Command '/forward' sent to @{BOT_USERNAME}.")
            
            # Fetch user details after starting the session
            usr_bot_me = await self.get_me()
            self.LOGGER(__name__).info(f"User session started. Logged in as: {usr_bot_me.first_name} (@{usr_bot_me.username}).")
            
            # Return the user instance and user ID
            return (self, usr_bot_me.id)
        except Exception as e:
            self.LOGGER(__name__).error(f"Error during user session start: {e}")
            raise

    async def stop(self, *args):
        '''Stop the user session and log the shutdown.'''
        self.LOGGER(__name__).info("Stopping the user session...")
        try:
            # Stop the client
            await super().stop()
            self.LOGGER(__name__).info("User session stopped successfully.")
        except Exception as e:
            self.LOGGER(__name__).error(f"Error during user session stop: {e}")
            raise
