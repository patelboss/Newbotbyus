from config import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME, LOGGER
from pymongo import MongoClient
from umongo import Instance, Document, fields

# Initialize the synchronous Mongo client
client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]
instance = Instance(db)

@instance.register
class SessionData(Document):
    id = fields.StrField(attribute='_id')  # Unique ID for the document
    phone_number = fields.StrField()  # Store phone number for session regeneration
    session = fields.StrField()  # Store the string session

    class Meta:
        collection_name = "sessions"  # This collection will store session data

# Synchronous functions for session handling

def save_string_session(session: str, phone_number: str = None):
    """
    Save the Pyrogram string session and the phone number (optional) in the database.
    """
    try:
        session_data = {"session": session}
        if phone_number:
            session_data["phone_number"] = phone_number  # Save the phone number for regeneration
        db.sessions.update_one(
            {"_id": "string_session"},
            {"$set": session_data},
            upsert=True
        )
        LOGGER(__name__).info("String session and credentials saved successfully.")
    except Exception as e:
        LOGGER(__name__).error(f"Error while saving string session: {e}")

def get_string_session():
    """
    Retrieve the Pyrogram string session from the database.
    """
    try:
        session = db.sessions.find_one({"_id": "string_session"})
        return session["session"] if session else None
    except Exception as e:
        LOGGER(__name__).error(f"Error while retrieving string session: {e}")
        return None

def get_credentials():
    """
    Retrieve the phone number used for generating the string session.
    """
    try:
        session = db.sessions.find_one({"_id": "string_session"})
        return session["phone_number"] if session else None
    except Exception as e:
        LOGGER(__name__).error(f"Error while retrieving credentials: {e}")
        return None

def save_credentials(phone_number: str):
    """
    Save the phone number used for generating the string session.
    """
    try:
        db.sessions.update_one(
            {"_id": "string_session"},
            {"$set": {"phone_number": phone_number}},
            upsert=True
        )
        LOGGER(__name__).info("Phone number saved successfully.")
    except Exception as e:
        LOGGER(__name__).error(f"Error while saving phone number: {e}")
