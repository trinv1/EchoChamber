
import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient

#Loading secrets from .env file
load_dotenv()

#Instantiates OpenAI client with API key from env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Instantiates Mongo client with uri key from env
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["SocialMediaDB"]
tweets = db["girlreddit"]

folder_dir = "/Users/trinvillaruel/Desktop/GScreenshotsReddit"

#Iterating over pictures in folder and building path
for image_name in os.listdir(folder_dir):
    if image_name.endswith(".png"):
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
                        "You extract ONLY the main Reddit post text from screenshots. "
                        "Respond EXACTLY in this JSON format and nothing else:\n"
                        "{\"post\": \"...\"}\n"
                        "Rules:\n"
                        "- NO markdown\n"
                        "- NO backticks\n"
                        "- NO explanations\n"
                        "- NO extra keys\n"
                        "- The value MUST be valid JSON string\n"
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Extract only the FIRST Reddit post's main text from this screenshot. "
                                "Ignore comments and sidebar content. Return plain text only."
                                "Respond with JSON only — no extra text."

                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                        }
                    ]
                }
            ]
        )

          #Extracting model output (JSON string)
        json_output = response.choices[0].message.content

        #Parsing JSON returned by model
        import json
        parsed = json.loads(json_output)
        post_text = parsed["post"]

        print(f"Extracted post:\n{post_text}\n")

        #Saving to MongoDB
        tweets.insert_one({
            "image_name": image_name,
            "tweet": post_text
        })

        print("Saved to MongoDB.\n")
