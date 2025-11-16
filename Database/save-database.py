from fastapi import FastAPI
from fastapi import HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["echochamber"]
tweets_collection = db["tweets"]

app = FastAPI()

@app.post("/")
def save_tweet(tweet: dict):
    try:
        result = tweets_collection.insert_one(tweet)
        return {"status": "success", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
