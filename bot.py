from pyrogram import Client
from pyrogram.enums import ParseMode
from config import BOT_TOKEN, API_ID, API_HASH, LOGGER, BOT_SESSION
#from database import get_string_session
#from utils import listen  # Import custom listen function
from pyromod import listen  # type: ignore
from user import User
import pyromod.listen
from plugins.directfd import forward_messages1
class Bot(Client):
    USER: User = None
    USER_ID: int = None

    def __init__(self):
        """Initialize the bot with enhanced logging for each step."""
        self.LOGGER = LOGGER
        self.LOGGER(__name__).info("Initializing the bot...")

        # Log information about the session and API credentials
        if BOT_SESSION:
            self.LOGGER(__name__).info("Using the provided BOT_SESSION for the bot.")
        else:
            self.LOGGER(__name__).warning("No BOT_SESSION provided. Using an in-memory session temporarily.")

        # Initialize the client
        super().__init__(
            BOT_SESSION,  # Pass session as the first argument
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            parse_mode=ParseMode.HTML,  # Set the default parse mode to HTML
            plugins={"root": "plugins"},
            workers=10
        )
        self.LOGGER(__name__).info("Bot initialization complete. Ready to start.")

    async def start(self):
        """Start the bot with detailed logging and necessary preparations."""
        self.LOGGER(__name__).info("Starting the bot...")
        try:
            await super().start()
            self.LOGGER(__name__).info("Successfully connected to Telegram servers.")

            # Fetch bot information
            me = await self.get_me()
            self.LOGGER(__name__).info(f"Bot details retrieved: Username: @{me.username}, Name: {me.first_name}.")

            # Log start completion
            self.LOGGER(__name__).info(f"Bot @{me.username} started successfully and is now online.")
            
            # Initialize User Client if required
            self.USER, self.USER_ID = await User().start()
            #self.LOGGER(__name__).info(f"Bot @{me.username} started successfully and is now online.")
            

        except Exception as e:
            self.LOGGER(__name__).error(f"An error occurred during bot startup: {e}")
            raise

    async def stop(self):
        """Stop the bot with clean shutdown and detailed logging."""
        self.LOGGER(__name__).info("Stopping the bot...")
        try:
            await super().stop()
            self.LOGGER(__name__).info("Bot has been disconnected from Telegram servers.")
            self.LOGGER(__name__).info("Bot stopped successfully. Goodbye!")
        except Exception as e:
            self.LOGGER(__name__).error(f"An error occurred during bot shutdown: {e}")
            raise
@Bot.USER.on_message(filters.create(lambda _, __, message: message.chat.id in [ch["source_id"] for ch in get_all_channels()]))
async def handle_message(client, message):
    """
    Handles incoming messages dynamically by verifying the source channel.
    """
    # Log the incoming message for debugging
    print(f" Bot User Received message from source channel {message.chat.id}: {message.text}")

    # Forward the message using the user account
    await forward_messages1(client, message)
