import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
import time
import json
import pymongo


#Loading secrets from .env file
load_dotenv()

#Instantiates OpenAI client with API key from env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Instantiates Mongo client with uri key from env
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["SocialMediaDB"]
boytweets = db["boytwitter"]
girltweets = db["girltwitter"]

batch_size = 5 #processing 5 images per batch
cursorgirl = girltweets.find({"image_name": "23-11-2025.png"})
cursorboy = boytweets.find({"image_name": "23-11-2025.png"})
cursorGirlList = list(cursorgirl)
cursorBoyList = list(cursorboy)

#Iterating over pictures in folder and building path
def sentiment_analysis(collection, cursor):

    for i in range(0, len(cursor), batch_size):
        batch = cursor[i:i + batch_size]
        print(f"\nProcessing batch:")
        time.sleep(3)

        for doc in batch:
            print(f"- {doc['_id']} : {doc['tweet']}")

            
            
        #Sleeping between batches to avoid tpm on api
        print("Batch finished. Sleeping 60 seconds\n")
        time.sleep(60)
        
        

sentiment_analysis(boytweets, cursorBoyList)
