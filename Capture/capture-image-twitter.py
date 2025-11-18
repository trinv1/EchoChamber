import os, time, pyautogui, schedule
from datetime import datetime

#Folders to save screenshots
TWITTER_BOY = "/Users/trinvillaruel/Desktop/BScreenshotsTwitter"
os.makedirs(TWITTER_BOY, exist_ok=True)

TWITTER_GIRL = "/Users/trinvillaruel/Desktop/GScreenshotsTwitter"
os.makedirs(TWITTER_GIRL, exist_ok=True)

#Function to take screenshots
def take_screenshots(file_path):
    for i in range(25):
        filename = f"screenshot-{i+1}.png"
        fullpath = os.path.join(file_path, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(fullpath)
        #time.sleep(1)

#Scheduling screenshots every Tuesday
schedule.every().tuesday.at("14:00").do(take_screenshots(TWITTER_BOY))
schedule.every().tuesday.at("14:03").do(take_screenshots(TWITTER_GIRL))

print("Screenshot scheduler started. Waiting for Sunday 14:00pm")

#Keeping scheduler running
while True:
    schedule.run_pending()
    time.sleep(30)

