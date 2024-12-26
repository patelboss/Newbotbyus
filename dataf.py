from pymongo import MongoClient

client = MongoClient(DATABASE_URI)
db = client["UserForwardBot"]
channels_col = db["channels"]

def add_channel(source_id, target_id):
    channels_col.update_one({"source_id": source_id}, {"$set": {"target_id": target_id}}, upsert=True)

def remove_channel(source_id):
    channels_col.delete_one({"source_id": source_id})

def get_all_channels():
    return channels_col.find()
