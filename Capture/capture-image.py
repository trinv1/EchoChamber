import os, time, pyautogui, schedule
from datetime import datetime

#Folder to save screenshots
SAVE_PATH = "/Users/trinvillaruel/Desktop/BScreenshots"
os.makedirs(SAVE_PATH, exist_ok=True)

#Function to take 3 screenshots in a row
def take_three_screenshots():
    for i in range(10):
        filename = f"screenshot_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{i+1}.png"
        fullpath = os.path.join(SAVE_PATH, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(fullpath)
        #time.sleep(1)

#Scheduling screenshots every Friday at 12:15 PM
schedule.every().friday.at("12:15").do(take_three_screenshots)

print("Screenshot scheduler started. Waiting for Friday 12:15pm")

#Keeping scheduler running
while True:
    schedule.run_pending()
    time.sleep(30)

