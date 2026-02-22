from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import os, traceback, time
from datetime import datetime, timezone
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from bson import Binary

load_dotenv()

#openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["SocialMediaDB"]
girltwitter = db["girltwitter"]
boytwitter = db["boytwitter"]
captures = db["captures"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Getting all tweets from boy account
@app.get("/tweets/boy")
def get_boy_tweets():
    data = list(boytwitter.find({}, {"_id": 0}))
    return {"count": len(data), "tweets": data}

#Getting all tweets from girl account
@app.get("/tweets/girl")
def get_girl_tweets():
    data = list(girltwitter.find({}, {"_id": 0}))
    return {"count": len(data), "tweets": data}

#Aggregating dates and political leaning
def counts_by_date_and_leaning(collection):
    pipeline = [
        #Creating "date_str" field from image_name and removing .png
        {
            "$addFields": {
                "date_str": {
                    "$replaceAll": {
                        "input": "$image_name",
                        "find": ".png",
                        "replacement": ""
                    }
                }
            }
        },
        #Grouping by date_str AND sentiment.political_leaning
        {
            "$group": {
                "_id": {
                    "date": "$date_str",
                    "leaning": "$sentiment.political_leaning"
                    },
                "count": {"$sum": 1}
            }
        },
        #Shaping output
        {
            "$project": {
                "_id": 0,
                "date": "$_id.date",
                "political_leaning": "$_id.leaning",
                "count": 1
            }
        },
        #Sorting by date 
        {"$sort": {"date": 1}}
    ]
    return list(collection.aggregate(pipeline))

@app.get("/stats/boy/political-leaning")
def boy_stats():
    result = counts_by_date_and_leaning(boytwitter)
    print("Boy stats:")
    for r in result:
        print(r)
    return {"series": result}

@app.get("/stats/girl/political-leaning")
def girl_stats():
    result = counts_by_date_and_leaning(girltwitter)
    print("Girl stats:")
    for r in result:
        print(r)
    return {"series": result}

os.makedirs("uploads", exist_ok=True)

#Endpoint to upload image
@app.post("/upload")
async def upload(
    image: UploadFile = File(...),
    tabId: str = Form(""),
    pageUrl: str = Form(""),
    ts: str = Form(""),
    account: str = Form(""),  
):
    data = await image.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty image")

    image_name = image.filename or f"{ts or int(datetime.now().timestamp())}.jpg"

    doc = {
        "created_at": datetime.now(timezone.utc),
        "image_name": image_name,
        "tabId": tabId,
        "pageUrl": pageUrl,
        "ts": ts,
        "account": account,
        "content_type": image.content_type or "image/jpeg",
        "image_bytes": Binary(data),
        "status": "queued",
        "tries": 0
    }

    ins = captures.insert_one(doc)
    return {"ok": True, "id": str(ins.inserted_id)}