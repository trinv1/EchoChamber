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
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a sentiment and political-alignment classifier. "
                                "Classify content based ONLY on language, framing, and expressed positions. "
                                "Do not apply moral judgment or assume correctness of any viewpoint. "

                                "LEFT-LEANING: "
                                "- emphasizes collective responsibility, systemic or structural explanations; "
                                "- focuses on equality, redistribution, or group-level outcomes; "
                                "- supports expanded government, regulation, or institutional intervention; "
                                "- uses framing aligned with progressive, socialist, or egalitarian traditions. "

                                "RIGHT-LEANING: "
                                "- emphasizes individual responsibility, national identity, or cultural continuity; "
                                "- focuses on sovereignty, borders, security, tradition, or market outcomes; "
                                "- supports limited government, enforcement, or established institutions; "
                                "- uses framing aligned with conservative, nationalist, or free-market traditions. "

                                "CENTRIST / MODERATE: "
                                "- balances or mixes left and right framing; "
                                "- focuses on pragmatism, trade-offs, or incremental change; "
                                "- avoids strong ideological or absolutist language. "

                                "APOLITICAL: "
                                "- contains no political claims, advocacy, or ideological framing; "
                                "- topics such as sports, entertainment, personal anecdotes, or non-political news. "

                                "UNCLEAR: "
                                "- insufficient or ambiguous information to infer political alignment. "

                                "Rules: "
                                "- Political alignment is inferred from the text itself, including both explicit ideological statements and implicit political signaling."
                                "- Implicit political signaling includes framing, narratives, or language commonly associated with contemporary political factions, even if no policy or ideology is explicitly stated."
                                "- Criticism of governments, religions, cultures, or ideologies is NOT inherently hateful."
                                "- Emotional tone and toxicity are independent of political alignment. "
                                "- Do not infer intent beyond the provided text. "

                                "Output JSON format:\n"
                                "{\n"
                                "  \"emotional_valence\": \"positive | neutral | negative | serious\",\n"
                                "  \"emotion_intensity\": 0.0 to 1.0,\n"
                                "  \"moral_stance\": \"supportive | condemning | informative | neutral | sarcastic\",\n"
                                "  \"political_leaning\": \"left | right | centre | apolitical | unclear\",\n"
                                "  \"is_toxic\": true | false,\n"
                                "  \"topic\": \"short neutral topic\"\n"
                                "}\n"
                            )
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Tweet: {tweet_text}\n\nAnalyse the sentiment and return JSON only."
                                }
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

