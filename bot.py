from pyrogram import Client
from pyrogram.enums import ParseMode
from config import BOT_TOKEN, API_ID, API_HASH, LOGGER, BOT_SESSION
from pyromod import listen  # type: ignore
from user import User  # Ensure User class is implemented correctly
#from plugins.directfd import setup_user_handlers

class Bot(Client):
    USER: User = None
    USER_ID: int = None

    def __init__(self):
        """Initialize the bot with enhanced logging."""
        self.LOGGER = LOGGER
        self.LOGGER(__name__).info("Initializing the bot...")
        self.USER = await User().start()  # Ensure User is initialized before plugin actions
        self.USER_ID = self.USER.me.id
        self.LOGGER(__name__).info(f"User client started with ID {self.USER_ID}.")
         #   setup_user_handlers(bot)
        

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
         #   self.USER = await User().start()  # Ensure User is initialized before plugin actions
          #  self.USER_ID = self.USER.me.id
          #  self.LOGGER(__name__).info(f"User client started with ID {self.USER_ID}.")
         #   setup_user_handlers(bot)

        except Exception as e:
            self.LOGGER(__name__).error(f"An error occurred during startup: {e}")
            raise

    async def stop(self):
        """Stop the bot and user client with clean shutdown."""
        self.LOGGER(__name__).info("Stopping the bot...")
        try:
            # Stop the user client if it exists
            if self.USER:
                await self.USER.stop()
                self.LOGGER(__name__).info("User client disconnected.")

            # Stop the bot client
            await super().stop()
            self.LOGGER(__name__).info("Bot has been disconnected from Telegram servers.")
            self.LOGGER(__name__).info("Bot stopped successfully. Goodbye!")
        except Exception as e:
            self.LOGGER(__name__).error(f"An error occurred during shutdown: {e}")
            raise
