import os, time, pyautogui, schedule
from datetime import datetime

#Folders to save screenshots
TWITTER_BOY = "/Users/trinvillaruel/Desktop/BScreenshotsTwitter"
os.makedirs(TWITTER_BOY, exist_ok=True)

TWITTER_GIRL = "/Users/trinvillaruel/Desktop/GScreenshotsTwitter"
os.makedirs(TWITTER_GIRL, exist_ok=True)

#Taking screenshots
def take_screenshots(file_path):
    for i in range(45):
        filename = f"{datetime.now().strftime('%d-%m-%Y')}_{i+1}.png"
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
schedule.every().tuesday.at("20:20").do(take_screenshots, TWITTER_BOY)
schedule.every().tuesday.at("20:25").do(take_screenshots, TWITTER_GIRL)
schedule.every().tuesday.at("19:00").do(delete_contents, TWITTER_GIRL)
schedule.every().tuesday.at("19:00").do(delete_contents, TWITTER_BOY)

print("Screenshot scheduler started. Waiting for Sunday 13:00pm")

#Keeping scheduler running
while True:
    schedule.run_pending()
    time.sleep(30)

