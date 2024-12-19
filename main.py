from flask import Flask
import threading
from bot import Bot  # Import Bot class from bot.py
from config import LOGGER

# Flask app for health check
health_app = Flask(__name__)

@health_app.route("/")
def health_check():
    return "Bot is healthy!", 200

def run_health_check_server():
    LOGGER(__name__).info("Starting health check server...")
    health_app.run(host="0.0.0.0", port=8080)

# Start both the bot and the health check server
def start():
    # Start health check server in a separate thread
    threading.Thread(target=run_health_check_server, daemon=True).start()
    
    # Start the bot
    LOGGER(__name__).info("Starting the bot...")
    bot = Bot()  # Create instance of Bot class (handles session generation)
    bot.run()

if __name__ == "__main__":
    LOGGER(__name__).info("Initializing the application...")
    start()
