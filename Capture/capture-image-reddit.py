import os, time, pyautogui, schedule
from datetime import datetime

#Folders to save screenshots
REDDIT_BOY = "/Users/trinvillaruel/Desktop/BScreenshotsReddit"
os.makedirs(REDDIT_BOY, exist_ok=True)

REDDIT_GIRL = "/Users/trinvillaruel/Desktop/GScreenshotsReddit"
os.makedirs(REDDIT_GIRL, exist_ok=True)

#Function to take screenshots
def take_screenshots_boy():
    for i in range(25):
        filename = f"screenshot-{i+1}.png"        
        fullpath = os.path.join(REDDIT_BOY, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(fullpath)
        #time.sleep(1)

#Function to take screenshots
def take_screenshots_girl():
    for i in range(25):
        filename = f"screenshot-{i+1}.png"
        fullpath = os.path.join(REDDIT_GIRL, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(fullpath)
        #time.sleep(1)

#Scheduling screenshots every Sunday
schedule.every().sunday.at("14:10").do(take_screenshots_boy)
schedule.every().sunday.at("14:15").do(take_screenshots_girl)


print("Screenshot scheduler started. Waiting for Sunday 14:10pm")

#Keeping scheduler running
while True:
    schedule.run_pending()
    time.sleep(30)

