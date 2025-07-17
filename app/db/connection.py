from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import dotenv_values
dotenv_path = ".env"
config = dotenv_values(dotenv_path=dotenv_path, encoding="utf-8-sig")
mongo_uri = config.get("MONGO_URL")

MONGO_URL1="mongodb+srv://flaamantimagemongo:flaamantimagemongo321@segmentimage.2gicwjo.mongodb.net/?retryWrites=false&w=majority&appName=SegmentImage"
client = MongoClient(
    MONGO_URL1, 
    server_api=ServerApi('1'),
    tls=True,
    tlsAllowInvalidCertificates=True
)

try:
    client.admin.command('ping')
    print("MongoDB connection successful.")
except Exception as e:
    print("MongoDB connection failed:", e)

# Export the database or collection you need
db = client.get_database("user_images")
users_collection = db["users"]