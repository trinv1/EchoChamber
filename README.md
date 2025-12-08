# EchoChamber

EchoChamber investigates how a personalised social-media feed evolves over time. It collects posts from Twitter (X) via capturing images from the recommendation feed and extracting text from the image. Sentiment analysis is then applied using the OpenAI API, and emotional trends are visualised over time using Streamlit dashboards.

This fully automated pipeline runs on a weekly schedule — capturing, processing, analysing, and visualising data with minimal manual input.

# Overview

* EchoChamber demonstrates an automated end-to-end data pipeline for studying algorithmic bias and polarisation in personalised social feeds.

* The workflow consists of:

* Data Capture – Fetch or screenshot posts from Twitter feed.

* Text Extraction – Extract visible text from screenshots.

* Storage – Save post content and metadata to a MongoDB Atlas database.

* Processing & Sentiment Analysis – Use OpenAI API to analyse tone and polarity.

* API Layer (FastAPI) – Provide structured access to stored text and sentiment results.

* Visualisation (Streamlit) – Display sentiment distribution and temporal trends interactively.

* Automation (Scheduler) – Execute the full pipeline weekly without manual intervention.

## Tech Stack

* Python
* Streamlit
* FastAPI
* GPT API
* Python scheduler
* MongoDB Atlas
