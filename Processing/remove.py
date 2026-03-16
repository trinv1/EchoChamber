from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["SocialMediaDB"]
boytweets = db["boytwitter"]
girltweets = db["girltwitter"]

def remove_png_suffix(collection, name):
    modified = 0

    cursor = collection.find(
        {"image_name": {"$regex": r"\.png$"}},
        {"_id": 1, "image_name": 1}
    )

    for doc in cursor:
        old = doc.get("image_name", "")
        new = old[:-4] if old.endswith(".png") else old

        if new != old:
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"image_name": new}}
            )
            modified += 1

    print(f"{name}: Modified {modified} documents")

remove_png_suffix(boytweets, "Boy")
remove_png_suffix(girltweets, "Girl")