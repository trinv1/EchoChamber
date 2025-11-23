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
        time.sleep(1)

#Deleting images in folder
def delete_contents(file_path):
    for image_name in os.listdir(file_path):
        if image_name.endswith(".png"):
            os.remove(os.path.join(file_path, image_name))

#Scheduling tasks every sunday
schedule.every().sunday.at("15:43").do(take_screenshots, TWITTER_BOY)
schedule.every().sunday.at("15:48").do(take_screenshots, TWITTER_GIRL)
schedule.every().sunday.at("17:00").do(delete_contents, TWITTER_GIRL)
schedule.every().sunday.at("17:00").do(delete_contents, TWITTER_BOY)

print("Screenshot scheduler started. Waiting for Sunday 15:00pm")

#Keeping scheduler running
while True:
    schedule.run_pending()
    time.sleep(30)

