# EchoChamber

EchoChamber is a research platform designed to analyse how personalised social media recommendation feeds evolve over time. The system captures content from the X (Twitter) “For You” feed, extracts text from screenshots, classifies sentiment and political leaning using large language models, and visualises trends through an interactive dashboard.

The project was developed to investigate whether gender-related account signals influence the political composition of recommended content.

Recorded demo of the application can be found at: [EchoChamber](https://atlantictu-my.sharepoint.com/personal/g00405393_atu_ie/_layouts/15/stream.aspx?id=%2Fpersonal%2Fg00405393_atu_ie%2FDocuments%2FVideos%2FClipchamp%2FVideo+Project+2%2FExports%2FEchoChamber.mp4&ga=1&referrer=StreamWebApp.Web&referrerScenario=AddressBarCopied.view.334b5991-674f-44c4-9f66-76f9478ee8aa)

# How to run
**Clone repository:**
* git clone https://github.com/trinv1/EchoChamber
* cd echochamber

**Install Dependencies:**
* pip install -r Backend/requirements.txt
* pip install -r requirements.txt

# Configuration 
* OPENAI_API_KEY=your_openai_key
* BREVO_API_KEY=your_brevo_key
* SECRET_KEY=your_secret_key
* MONGO_URI=your_mongodb_connection_string

# How to start
1. Open streamlit app: https://echochamber.streamlit.app/
* Create account
* Login

2. Load extension by going to: chrome://extensions/
* Enable Developer Mode
* Click “Load unpacked”
* Select the extension/ folder from this project

# Tech Stack
* Python
* FastAPI
* Streamlit
* MongoDB Atlas
* OpenAI API
* Chrome Extension (JavaScript, Manifest V3)

# Overview
EchoChamber analyses how personalised X (Twitter) feeds evolve over time using automated capture, AI-based text extraction, and sentiment classification.

# System Overview
* Chrome extension captures feed screenshots
* Backend processes and classifies content
* MongoDB stores structured data
* Streamlit visualises results

# Experimental Design 
* Multi-phase controlled accounts
* One variable changed per phase
* Tracks impact on political content



