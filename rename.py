import os, time, pyautogui, schedule
from datetime import datetime

TWITTER_BOY = "/Users/trinvillaruel/Desktop/BScreenshotsTwitter"
os.makedirs(TWITTER_BOY, exist_ok=True)

#Function to take screenshots
def wse(file_path):
    for i in range(2):
        filename = f"screenshot-{i+1}.png"        
        fullpath = os.path.join(file_path, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(fullpath)
        time.sleep(1)

#Deleting images in folder
def rename(file_path):
    for i in range(42):
        filename = f"screenshot_{datetime.now().strftime('%d-%m-%Y')}_{i+1}.png"
        for image_name in os.listdir(file_path):
            if image_name.endswith(".png"):
                os.rename(os.path.join(file_path, image_name), os.path.join(file_path, filename))

rename(TWITTER_BOY)