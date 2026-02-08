from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from datetime import datetime
from pymongo import MongoClient
import uvicorn
from dotenv import load_dotenv
import os
from openai import OpenAI
import base64
import json
from datetime import datetime, timezone

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["SocialMediaDB"]
girltwitter = db["girltwitter"]
boytwitter = db["boytwitter"]

app = FastAPI()

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

@app.post("/ingest-screenshot")
async def ingest_screenshot(
    image: UploadFile = File(...),     # the PNG from the extension
    profile: str = Form(...),          # "boy" or "girl"
    url: str = Form(""),               # optional metadata from extension
    title: str = Form("")              # optional metadata from extension
):
    # 1) Validate profile
    profile = profile.lower().strip()
    if profile not in {"boy", "girl"}:
        raise HTTPException(status_code=400, detail="profile must be 'boy' or 'girl'")

    # 2) Choose Mongo collection based on profile
    collection = boytwitter if profile == "boy" else girltwitter

    # 3) Create a timestamp-based image_name (keeps your existing stats pipeline compatible)
    image_name = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")[:-3] + ".png"

    # 4) Read the uploaded image bytes into memory (NO saving to disk)
    image_bytes = await image.read()

    # 5) Base64 encode (same as your script)
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # 6) Call OpenAI to extract the FIRST main tweet in the screenshot
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
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
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
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
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}"
                        }
                    }
                ]
            }
        ]
    )

    # 7) Parse model output
    json_output = response.choices[0].message.content

    try:
        parsed = json.loads(json_output)
    except json.JSONDecodeError:
        # Store the raw output so you can debug failures
        collection.insert_one({
            "image_name": image_name,
            "profile": profile,
            "url": url,
            "title": title,
            "raw_model_output": json_output,
            "status": "parse_error",
            "created_at": datetime.now(datetime.timezone.utc)()
        })
        raise HTTPException(status_code=500, detail="Model returned invalid JSON")

    # 8) Save to Mongo (same fields you used before + metadata)
    doc = {
        "image_name": image_name,
        "username": parsed.get("username", ""),
        "display_name": parsed.get("display_name", ""),
        "tweet": parsed.get("tweet", ""),
        "likes": parsed.get("likes", ""),
        "retweets": parsed.get("retweets", ""),
    }
    collection.insert_one(doc)

    # 9) Done — image bytes are discarded automatically after request ends
    return {"ok": True, "profile": profile, "image_name": image_name}



