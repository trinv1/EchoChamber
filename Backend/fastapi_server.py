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

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PROCESSOR_ENABLED = os.getenv("PROCESSOR_ENABLED", "0") == "1"

MONGO_URI = os.getenv("MONGO_URI")

BATCH_SIZE = 5
BATCH_SLEEP_SEC = 60
IDLE_SLEEP_SEC = 3

SYSTEM_PROMPT = (
    "You are a Twitter screenshot parser. "
    "Extract ONLY the FIRST main tweet visible in the screenshot. "
    "Return ONLY valid JSON. No markdown, no backticks, no explanations.\n"
    "{\n"
    "  \"username\": \"\",\n"
    "  \"display_name\": \"\",\n"
    "  \"tweet\": \"\",\n"
    "  \"likes\": \"\",\n"
    "  \"retweets\": \"\",\n"
    "  \"replies\": \"\"\n"
    "}\n"
)

USER_PROMPT = (
    "Extract all visible information for ONLY the first main tweet. "
    "Do NOT include replies unless they are part of the first tweet. "
    "Required fields:\n"
    "- username (@handle)\n"
    "- display_name\n"
    "- tweet text\n"
    "- likes count\n"
    "- retweets count\n"
    "Return ONLY valid JSON. No extra text."
)

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

#Endpoint to check server can see queued docs
@app.get("/debug/queue")
def debug_queue():
    q = list(captures.find({"status": "queued"}, {"image_bytes": 0, "_id": 0}).sort("created_at", 1).limit(5))
    return {"queued_sample": q, "queued_count": captures.count_documents({"status": "queued"})}

def process_one_capture(doc):
    #1 read image bytes
    #2 call OpenAI vision to extract JSON
    #3 insert into boytwitter or girltwitter
    #4 update captures status to done/error
    pass

@app.post("/process/one")
def process_one():
    doc = captures.find_one({"status": "queued"})
    if not doc:
        return {"ok": True, "msg": "nothing queued"}

    # call your process_one_capture(doc) here (we’ll wire next)
    return {"ok": True, "id": str(doc["_id"])}
