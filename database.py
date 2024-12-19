from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from config import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME, LOGGER

# Initialize the database client and instance
client = AsyncIOMotorClient(DATABASE_URI)  # Ensure using the async MongoDB client
db = client[DATABASE_NAME]
instance = Instance(db)

# Register the data models for storing session and credentials
@instance.register
class Data(Document):
    id = fields.StrField(attribute='_id')  # Unique ID for the document
    channel = fields.StrField()
    file_type = fields.StrField()
    message_id = fields.IntField()
    use = fields.StrField()
    methord = fields.StrField()
    caption = fields.StrField()

    class Meta:
        collection_name = "forwarddata"  # Fixed collection name to avoid confusion

# Ensure Data is properly initialized
#if db is None:
#    raise Exception("Database connection is not properly initialized.")

#if Data.collection is None:
#    raise Exception("Collection reference is not properly initialized.")
    
async def save_data(id, channel, message_id, methord, caption, file_type):
    """
    Save a document in the database.
    """
    try:
        data = Data(
            id=id,
            use="forward",
            channel=channel,
            message_id=message_id,
            methord=methord,
            caption=caption,
            file_type=file_type
        )
        await data.commit()
        LOGGER(__name__).info("Message saved in database successfully.")
    except ValidationError as e:
        LOGGER(__name__).error(f"Validation error: {e.messages}")
    except DuplicateKeyError:
        LOGGER(__name__).warning("Document already exists in the database.")
    except Exception as e:
        LOGGER(__name__).error(f"Unexpected error while saving data: {e}")

async def get_search_results():
    """
    Fetch the latest document matching the filter.
    """
    try:
        filter_criteria = {'use': "forward"}
        cursor = Data.find(filter_criteria)
        cursor.sort('$natural', -1)  # Sort in descending order
        cursor.skip(0).limit(1)  # Limit to one result
        messages = await cursor.to_list(length=1)
        return messages
    except Exception as e:
        LOGGER(__name__).error(f"Error while fetching search results: {e}")
        return []
