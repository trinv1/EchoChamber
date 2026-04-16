from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timezone


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["SocialMediaDB"]
tweets = db["tweets"]

for subject_id in ["1", "2"]:
    count = tweets.count_documents({"subject_id": subject_id})
    print(f"Subject {subject_id}: {count} tweets")