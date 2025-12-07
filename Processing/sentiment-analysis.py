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

#Only finding tweets that arent analysed yet
cursorgirl = girltweets.find({"sentiment": {"$exists": False}})
cursorboy = boytweets.find({"sentiment": {"$exists": False}})
cursorGirlList = list(cursorgirl)
cursorBoyList = list(cursorboy)

#Analysing sentiment of tweets
def sentiment_analysis(collection, cursor):

        #Looping through documents in batches
        for i in range(0, len(cursor), batch_size):
            batch = cursor[i:i + batch_size]
            print(f"\nProcessing batch:")

            for doc in batch:
                print(f"- {doc['_id']} : {doc['tweet']}")
                tweet_text = doc["tweet"]

                #Calling API and creating chat completion request
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    #Prompt
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a sentiment and political-alignment classifier."
                                "Classify content using these political categories:"
                                "LEFT-LEANING: "
                                "- supports social justice, equality, minority rights; "
                                "- pro-Palestine, anti-war, anti-genocide framing; "
                                "- pro-LGBTQ+, pro-immigration, asylum advocacy; "
                                "- criticism of police, capitalism, corporations, or right-wing governments; "
                                "- humanitarian framing such as 'this is genocide', 'we need ceasefire', 'protect civilians'. "
                                
                                "RIGHT-LEANING: "
                                "- nationalism, anti-immigration, anti-asylum narratives; "
                                "- strong criticism of Islam, Muslims, or Middle Eastern cultures; "
                                "- strong criticism of any ethnic cultures or backgrounds/minorities in general; "
                                "- pro-police, pro-military, pro-border enforcement; "
                                "- support for Trump, conservatives, patriotism framing; "
                                "- cultural traditionalism, anti-woke, anti-LGBTQ+ framing. "

                                "CENTRIST / MODERATE: "
                                "- balanced or neutral anguage; "
                                "- avoids ideological framing; "
                                "- reports facts without advocacy; "
                                "- political commentary without emotional bias. "

                                "APOLITICAL: "
                                "- content unrelated to politics; "
                                "- entertainment, sports, memes, neutral news etc. "

                                "UNCLEAR: "
                                "- insufficient information to determine leaning. "

                                "Rules: "
                                "- Toxicity is separate from political leaning. "
                                "- Criticism of governments, religions, or ideologies is NOT automatically hateful. "
                                "- Identify the ideological alignment of the message, not the sentiment tone. "
                                "Output JSON format:\n"
                                "{\n"
                                "  \"emotional_valence\": \"positive | neutral | negative | serious\",\n"
                                "  \"emotion_intensity\": 0 to 1,\n"
                                "  \"moral_stance\": \"supportive | condemning | informative | neutral | sarcastic\",\n"
                                "  \"political_leaning\": \"left | right | centre | unclear | apolitical\",\n"
                                "  \"is_toxic\": false,\n"
                                "  \"topic\": \"short category\"\n"
                                "}\n"
                            )
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Tweet: {tweet_text}\n\nAnalyse the sentiment and return JSON only."                                                  
                                },
                            ]
                        }
                    ]
                )

                #Extracting model output (JSON string)
                sentiment = json.loads(response.choices[0].message.content)

                print(f"Sentiment:\n{sentiment}\n")

                #Updating docs in mongo with sentiment
                collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"sentiment": sentiment}}
            )

            print("Saved to MongoDB.\n")
                
            #Sleeping between batches to avoid tpm on api
            print("Batch finished. Sleeping 60 seconds\n")
            time.sleep(60)
        

sentiment_analysis(girltweets, cursorGirlList)
sentiment_analysis(boytweets, cursorBoyList)

