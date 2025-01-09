from pyrogram import Client
from pyrogram.enums import ParseMode
from config import BOT_TOKEN, API_ID, API_HASH, LOGGER, BOT_SESSION
from pyromod import listen  # type: ignore
from user import User  # Ensure User class is implemented correctly
# from plugins.directfd import setup_user_handlers

class Bot(Client):
    USER: Client = None  # Initially None, dynamically assigned later
    USER_ID: int = None

    def __init__(self):
        """Initialize the bot with enhanced logging."""
        self.LOGGER = LOGGER
        self.LOGGER(__name__).info("Initializing the bot...")
        
        # Log session information
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
        self.LOGGER(__name__).info("Bot initialization complete.")

    @property
    def user_client(self):
        """Provide a fallback user client (bot client) if the user client is not initialized."""
        return self.USER or self  # Fallback to bot client if USER is not ready

    async def start(self):
        """Start the bot and user account client."""
        self.LOGGER(__name__).info("Starting the bot...")
        try:
            # Start the bot client
            await super().start()
            self.LOGGER(__name__).info("Bot client connected to Telegram servers.")

            # Fetch bot information
            me = await self.get_me()
            self.LOGGER(__name__).info(f"Bot started as @{me.username} ({me.id}).")

            # Start the user client
            try:
                user_instance = User()
                self.USER = await user_instance.start()  # Attempt to initialize the User client
                self.USER_ID = self.USER.me.id
                self.LOGGER(__name__).info(f"User client started with ID {self.USER_ID}.")
            except Exception as user_error:
                self.LOGGER(__name__).warning(f"User client initialization failed: {user_error}")
                self.USER = None  # Keep USER as None for fallback logic

        except Exception as e:
            self.LOGGER(__name__).error(f"An error occurred during startup: {e}")
            raise

    async def stop(self):
        """Stop the bot and user client with clean shutdown."""
        self.LOGGER(__name__).info("Stopping the bot...")
        try:
            # Stop the user client if it exists
            if self.USER and self.USER != self:  # Ensure we don't stop the fallback client
                await self.USER.stop()
                self.LOGGER(__name__).info("User client disconnected.")

            # Stop the bot client
            await super().stop()
            self.LOGGER(__name__).info("Bot has been disconnected from Telegram servers.")
            self.LOGGER(__name__).info("Bot stopped successfully. Goodbye!")
        except Exception as e:
            self.LOGGER(__name__).error(f"An error occurred during shutdown: {e}")
            raise
