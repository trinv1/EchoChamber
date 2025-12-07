import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
import time
import json


#Loading secrets from .env file
load_dotenv()

#Instantiates OpenAI client with API key from env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Instantiates Mongo client with uri key from env
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["SocialMediaDB"]
boytweets = db["boytwitter"]
girltweets = db["girltwitter"]

folder_boy = "/Users/trinvillaruel/Desktop/BScreenshotsTwitter"
folder_girl = "/Users/trinvillaruel/Desktop/GScreenshotsTwitter"

batch_size = 5 #processing 5 images per batch

#Iterating over pictures in folder and building path
def extract_text(folder_dir, collection):

    #list of images
    files = [f for f in os.listdir(folder_dir) if f.lower().endswith(".png")]
    
    #Looping through files in batches
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        print(f"\nProcessing batch: {batch}")

        for image_name in batch:
            image_path = os.path.join(folder_dir, image_name)
            print(f"Processing: {image_name}")

            #Reading and base64-encoding image
            with open(image_path, "rb") as img_file:
                image_bytes = img_file.read()
                image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            #Calling API and creating chat completion request
            response = client.chat.completions.create(
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

            #Extracting model output (JSON string)
            json_output = response.choices[0].message.content

            #Parsing JSON returned by model
            parsed = json.loads(json_output)
            tweet_text = parsed["tweet"]

            print(f"Extracted tweet:\n{tweet_text}\n")

            #Saving to MongoDB
            collection.insert_one({
            "image_name": image_name,
            "username": parsed.get("username", ""),
            "display_name": parsed.get("display_name", ""),
            "tweet": parsed.get("tweet", ""),
            "likes": parsed.get("likes", ""),
            "retweets": parsed.get("retweets", ""),
        })

        print("Saved to MongoDB.\n")
            
        #Sleeping between batches to avoid tpm on api
        print("Batch finished. Sleeping 60 seconds\n")
        time.sleep(60)

extract_text(folder_girl, girltweets)
extract_text(folder_boy, boytweets)