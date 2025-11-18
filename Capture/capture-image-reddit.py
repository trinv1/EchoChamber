import os, time, pyautogui, schedule
from datetime import datetime

#Folders to save screenshots
REDDIT_BOY = "/Users/trinvillaruel/Desktop/BScreenshotsReddit"
os.makedirs(REDDIT_BOY, exist_ok=True)

REDDIT_GIRL = "/Users/trinvillaruel/Desktop/GScreenshotsReddit"
os.makedirs(REDDIT_GIRL, exist_ok=True)

#Function to take screenshots
def take_screenshots(file_path):
    for i in range(2):
        filename = f"screenshot-{i+1}.png"        
        fullpath = os.path.join(file_path, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(fullpath)
        time.sleep(1)

#Scheduling screenshots every Tuesday
schedule.every().tuesday.at("14:06").do(take_screenshots(REDDIT_BOY))
schedule.every().tuesday.at("14:09").do(take_screenshots(REDDIT_GIRL))

print("Screenshot scheduler started. Waiting for Sunday 14:10pm")

#Keeping scheduler running
while True:
    schedule.run_pending()
    time.sleep(30)

