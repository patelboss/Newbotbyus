import os
import logging

# Environment Variables
API_ID = int(os.environ.get("API_ID", 0))  # Default to 0 if not set
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "none")
BOT_SESSION = os.environ.get("BOT_SESSION", "Forward_BOT")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))  # Default to 0 if not set
DATABASE_URI = os.environ.get("DATABASE_URI", "")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "Cluster0")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "Forward_data")
SESSION = os.environ.get("SESSION", "BQE0_ZkAjmev5JZRKYZQfyJPD_pZdpzpa22I9SS2RmYXl6kKQJjnFYJjm2IJVWABMdo-zNPWIS33gk82FbpZMKjD97KeFBz1JNM8CQTfQ7sm_GuR5hgfir5ccRuKyyLUXKumpfFm35KhJzpThBORq-jKyr5SXX1qwCSerzKX7yAln1AkVoK77VP8HyIFy3dRK5RZWa1XpHPuRWLX8neiCoun3Xh9BlA8hmD-29gATa3q4ryKL3MeD0Vg9g6FgB3ao3c5zIGb7o0zkhFbdnyg3t_w8q-xgucT8YbWoLmVO0pdeDmT-Bi3kPogmUCSpDF0iAhuc8IeqTe4PohPgooiUGR_268HIQAAAAB-RdJ7AA")
TO_CHANNEL = int(os.environ.get("TO_CHANNEL", 0)) 
print(f"To Channel : {TO_CHANNEL}") #Default to 0 if not set

# Logger Function
def LOGGER(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    return logger

# Additional Check for Environment Variables
if not DATABASE_URI or not DATABASE_NAME:
    raise ValueError("DATABASE_URI or DATABASE_NAME is not set correctly in the environment variables.")
