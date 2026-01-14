import streamlit as st
import requests


st.title("Algorithmic Bias Analysis")

API_URL_B = "http://127.0.0.1:8000/stats/boy/political-leaning"
API_URL_G = "http://127.0.0.1:8000/tweets/girl"

st.area_chart

try:
    response_boy = requests.get(API_URL_B)
    response_boy.raise_for_status()#raise error if failure
    data_boy = response_boy.json()

    response_girl = requests.get(API_URL_G)
    response_girl.raise_for_status()#raise error if failure
    data_girl = response_girl.json()

    st.success("Connected to FastAPI")

    st.write("Tweet count boy:", data_boy["count"])
    #Showing first 5 tweets
    st.json(data_boy["tweets"][:5])

    st.write("Tweet count girl:", data_girl["count"])
   # st.json(data_girl["tweets"][:5])


except Exception as e:
    st.error("Failed to connect to FastAPI")
    st.write(e)
