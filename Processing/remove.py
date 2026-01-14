from pymongo import MongoClient
import os
import re
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["SocialMediaDB"]
boytweets = db["boytwitter"]
girltweets = db["girltwitter"]

# pattern: "_<digits>.png" at the end of the string
PATTERN = re.compile(r"_(\d+)\.png$")

def clean_image_names(collection, name):
    modified = 0

    # Only pull the docs that actually need fixing
    cursor = collection.find(
        {"image_name": {"$regex": r"_\d+\.png$"}},
        {"_id": 1, "image_name": 1}
    )

    for doc in cursor:
        old = doc["image_name"]
        new = PATTERN.sub(".png", old)

        if new != old:
            collection.update_one({"_id": doc["_id"]}, {"$set": {"image_name": new}})
            modified += 1

    print(f"{name}: Modified {modified} documents")

clean_image_names(boytweets, "Boy")
clean_image_names(girltweets, "Girl")
