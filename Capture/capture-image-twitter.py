import os, time, pyautogui, schedule
from datetime import datetime

#Folders to save screenshots
TWITTER_BOY = "/Users/trinvillaruel/Desktop/BScreenshotsTwitter"
os.makedirs(TWITTER_BOY, exist_ok=True)

TWITTER_GIRL = "/Users/trinvillaruel/Desktop/GScreenshotsTwitter"
os.makedirs(TWITTER_GIRL, exist_ok=True)

#Function to take screenshots
def take_screenshots_boy():
    for i in range(25):
        filename = f"screenshot_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{i+1}.png"
        fullpath = os.path.join(TWITTER_BOY, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(fullpath)
        #time.sleep(1)

#Function to take screenshots
def take_screenshots_girl():
    for i in range(25):
        filename = f"screenshot_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{i+1}.png"
        fullpath = os.path.join(TWITTER_GIRL, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(fullpath)
        #time.sleep(1)

#Scheduling screenshots every Sunday
schedule.every().sunday.at("14:00").do(take_screenshots_boy)
schedule.every().sunday.at("14:05").do(take_screenshots_girl)


print("Screenshot scheduler started. Waiting for Friday 12:15pm")

#Keeping scheduler running
while True:
    schedule.run_pending()
    time.sleep(30)

