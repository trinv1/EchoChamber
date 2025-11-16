import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

#Loading secrets from .env file
load_dotenv()

#Instantiates OpenAI client with API key from env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

folder_dir = "/Users/trinvillaruel/Desktop/BScreenshots"

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
                    #Setting strict behaviour
                    "role": "system",
                    "content": "You extract only the tweet text from screenshots of Twitter/X feeds."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (#Defining output format
                                "Extract only the main tweet text from this screenshot. "
                                "If more than one tweet appears, extract only the very first main tweet shown. "
                                "Ignore usernames, metrics, timestamps, menus, or UI elements. "
                                "Return plain text only — one line per tweet."
                            )
                        },
                        {
                            #Passing image input as data url so openai servers can see it
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ]
        )

        #Pulling text output 
        extracted_text = response.choices[0].message.content
        
        print(f"\nExtracted text:\n{extracted_text}\n")

        #Extracted text folder
        et_folder = "/Users/trinvillaruel/Desktop/Extracted text"
        
        #Saving result
        output_path = os.path.join(et_folder, f"{os.path.splitext(image_name)[0]}_text.txt")
        with open(output_path, "w") as f:
            f.write(extracted_text)
