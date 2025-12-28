from pymongo import MongoClient
import os

from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["SocialMediaDB"]
boytweets = db["boytwitter"]
girltweets = db["girltwitter"]

# Remove 'sentiment' field from all documents
result = boytweets.update_many(
    {"sentiment": {"$exists": True}},
    {"$unset": {"sentiment": ""}}
)

result2 = girltweets.update_many(
    {"sentiment": {"$exists": True}},
    {"$unset": {"sentiment": ""}}
)

print(f"Modified documents: {result.modified_count}")
print(f"Modified documents: {result2.modified_count}")

