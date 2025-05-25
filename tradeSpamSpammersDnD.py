import pyautogui
import threading
import time
import pytesseract
import random
from PIL import Image
#https://github.com/Sanoras1/tradeSpamSpammersDnD/tree/main

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pyautogui.FAILSAFE = True
name_lock = threading.Lock()
beginFindName = True
name = []
inputNameHasRan = False
screenshotList = []
screenshotCreate5HasRan = False

def screenshotCreate5():
     global screenshotList, screenshotCreate5HasRan
     screenshotList.clear()
     for index in range(5):
          screenshotName = f"tradeSpamScreenshot{index}.png"
          pyautogui.screenshot(screenshotName)
          screenshotList.append(screenshotName)
          print("screenshot saved {screenshotName}")
     for screenshot_path in screenshotList:
          image = Image.open(screenshot_path)
          image = image.crop(box=[1000,565,1550,865])
          image.save(screenshot_path)
          print("cropped list")
          time.sleep(0.1)
     screenshotCreate5HasRan = True
     time.sleep(10)
 
def findName():
    global beginFindName, name, screenshotList, screenshotCreate5HasRan
    if screenshotCreate5HasRan:
     for screenshotIndex in range(5):
          screenShot = screenshotList[screenshotIndex]
          text = pytesseract.image_to_string(screenShot)
          print(text)
          index = text.find("has requested")
          if index != -1:
               before_tradeText = text[:index].strip()
               words = before_tradeText.split()
               if words:
                    possibleName = words[-1]
                    print(f"Name detected: {possibleName}")
                    with name_lock:
                         if possibleName not in name: 
                              name.append(possibleName)
                              print(name)
                              beginFindName = False
               else:
                    print("scanning text...")
          else:
               print ("trade text not found")

          time.sleep(1)

def inputName():
        global beginFindName
        global inputNameHasRan
        global name
        currentNameIndex = 0
        while True:
             with name_lock:
                  if name:
                       currentName = name[currentNameIndex % len(name)]
                       print(f"trading with: {currentName}")
                       pyautogui.moveTo(1400,822)
                       pyautogui.click()
                       pyautogui.moveTo(2250, 1350)
                       pyautogui.click()
                       pyautogui.hotkey('ctrl', 'a')
                       pyautogui.write(currentName)
                       inputNameHasRan = True
                       time.sleep(10)
                       currentNameIndex += 1
                       beginFindName = True


def spamTrader():
     numOfTrades = 0
     insult = ["you are stinky", "u suk", "im goonin rn", "im wastin your time bub", "rent free big dawg...", "fortnite balls", "you like cd's? Cee Dee's nuts",
               "when u trading...", "<3 I like tradin you :)"]
     while True:
          if inputNameHasRan:
               pyautogui.moveTo(2155,353)
               pyautogui.rightClick()
               pyautogui.moveTo(2210,400)
               pyautogui.click()
               numOfTrades = numOfTrades + 1
               if numOfTrades % 50 == 0:
                    print(f"{numOfTrades} trades completed.")
                    pyautogui.moveTo(180,1365)
                    pyautogui.click()
                    pyautogui.write(insult[random.randint(0,8)])
                    pyautogui.press('enter')
                    time.sleep(10)
                    print("continuing...")
          time.sleep(0.0125)

thread1 = threading.Thread(target=inputName, daemon=True)
thread1.start()
thread2 = threading.Thread(target=findName, daemon=True)
thread2.start()
thread3 = threading.Thread(target=spamTrader, daemon=True)
thread3.start()
thread4 = threading.Thread(target=screenshotCreate5, daemon=True)
thread4.start()

while True:
    time.sleep(1)

