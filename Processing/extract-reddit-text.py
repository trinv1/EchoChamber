
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
                        "You extract structured Reddit post data from screenshots. "
                        "Extract ALL visible posts from top to bottom. "
                        "Return EXACTLY this JSON format and nothing else:\n"
                        "{\n"
                        "  \"posts\": [\n"
                        "    {\n"
                        "      \"subreddit\": \"name of the subreddit\",\n"
                        "      \"username\": \"author username (without u/)\",\n"
                        "      \"upvotes\": \"number of upvotes (integer only)\",\n"
                        "      \"downvotes\": null,\n"
                        "      \"text\": \"main post text only\"\n"
                        "    }\n"
                        "  ]\n"
                        "}\n"
                        "Rules:\n"
                        "- Only include actual posts, not ads or sponsored content.\n"
                        "- Extract ONLY the main post text (no comments, vote buttons, share icons, or UI elements).\n"
                        "- Extract subreddit names exactly as shown (e.g., r/Python → \"Python\").\n"
                        "- Extract usernames exactly as shown (if none visible, set username to null).\n"
                        "- Reddit does not show downvotes, so always return: \"downvotes\": null.\n"
                        "- Upvotes must be integers only (e.g., \"172\").\n"
                        "- NO markdown.\n"
                        "- NO backticks.\n"
                        "- NO explanations.\n"
                        "- NO extra keys.\n"
                        "- JSON must be valid and parseable.\n"
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Extract ALL visible Reddit posts from this screenshot. "
                                "Return subreddit name, username, upvotes, downvotes, and post text. "
                                "Follow the JSON schema exactly. "
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
    posts_text = parsed["posts"]

    print(f"Extracted post:\n{posts_text}\n")

    #Saving to MongoDB
    tweets.insert_one({
        "image_name": image_name,
        "tweet": posts_text
    })

    print("Saved to MongoDB.\n")
