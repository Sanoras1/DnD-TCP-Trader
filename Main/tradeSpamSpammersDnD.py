import pyautogui
import threading
import time
import pytesseract
import random
from PIL import Image
import json
import os
#https://github.com/Sanoras1/tradeSpamSpammersDnD/tree/main

#pip install opencv-python(gives numpy64int make sure to convert)
#CONFIG
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pyautogui.FAILSAFE = True
jsonFile = "usernamesList.json"

# Path setup for image assets
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, '..', 'assets')

#Flags/threading
name_lock = threading.Lock()
beginFindName = True
inputNameHasRan = False
name = []
screenshotList = []
screenshotCreate5HasRan = False
box = ()
box1 = ()
box2 = ()
imageForLocation = os.path.join(ASSETS_DIR, "tempRect.png")
imageForChatLoc = os.path.join(ASSETS_DIR, "imageOfChatBar.png")
imageForFirst = os.path.join(ASSETS_DIR, "imageForFirst.png")

#JSON FUNCT
def loadUsernames():
     if not os.path.exists(jsonFile):
          with open(jsonFile, "w") as f:
               json.dump([], f)
     with open(jsonFile, "r") as f:
          return json.load(f)
     
def appendUsername(newTr):
     usernames = loadUsernames()
     if newTr not in usernames:
          usernames.append(newTr)
          with open(jsonFile, "w") as f:
               json.dump(usernames, f, indent = 2)
          print(f"Added {newTr} to usernames list.")
     else:
          print(f"{newTr} already on file.")

#setup locations for each click
def findRect(imageOfRect):
     global box
     while box == ():
          box = pyautogui.locateOnScreen(imageOfRect, confidence=0.8)
          if box:
               box = (int(box.left), int(box.top), box.width, box.height)
               print(f"rectangle found at: {box}")
          else:
               print("rectangle not found")
#finds location of chat bar (area next to send button for sending "insults")
def findChat(iChatBar):
     global box1
     while box1 == ():
          box1 = pyautogui.locateOnScreen(iChatBar, confidence=0.8)
          if box1:
               box1 = (int(box1.left), int(box1.top), box1.width, box1.height)
               print(f"Chat bar found at: {box1}")
          else:
               print("Chat bar not found.")
#finds location of the first player who shows up after entering someone's name in search
def findFirst(iForFirst):
    global box2
    while box2 == ():
        box2 = pyautogui.locateOnScreen(iForFirst, confidence=0.8)
        if box2:
            box2 = (int(box2.left), int(box2.top), box2.width, box2.height)
            print(f"First slot found at: {box2}")
        else:
            print("first not found")

findRect(imageForLocation)
#findChat(imageForChatLoc)     Commented out. Not in current use--
#findFirst(imageForFirst)
#start of threaded functions
def screenshotCreate5():
     global screenshotList, screenshotCreate5HasRan, box
     while True:
          if not box:
               print("waiting for rectangle to be found...")
               time.sleep(2)
               continue
          screenshotList.clear()
          for index in range(5):
               screenshotName = f"tradeSpamScreenshot{index}.png"
               pyautogui.screenshot(region = box).save(screenshotName)
               screenshotList.append(screenshotName)
               print(f"screenshot saved {screenshotName}")
               time.sleep(0.05)
          screenshotCreate5HasRan = True
          time.sleep(10)
 
def findName():
    global beginFindName, name, screenshotList, screenshotCreate5HasRan
    time.sleep(10)
    name[:] = loadUsernames()
    while True:
     if screenshotCreate5HasRan:
          for screenshotIndex in range(5):
               screenShot = screenshotList[screenshotIndex]
               try:
                    text = pytesseract.image_to_string(screenShot)
                    print(f"OCR result from screenshot {screenshotIndex}:")
                    print(text)
               except Exception as e:
                    print(f"OCR failed on screenshot {screenshotIndex}: {e}")
                    continue

               index = text.find("has requested")
               if index != -1:
                    before_tradeText = text[:index].strip()
                    words = before_tradeText.split()
                    if words:
                         possibleName = words[-1]
                         print(f"Name detected: {possibleName}")
                         with name_lock:
                              if possibleName not in name: 
                                   appendUsername(possibleName)
                                   name.append(possibleName)
                                   beginFindName = False
                    else:
                         print("Text found but no name extracted")
               else:
                    print ("trade text not found")
     screenshotCreate5HasRan = False
     time.sleep(1)

def inputName():
        global beginFindName
        global inputNameHasRan
        global name
        currentNameIndex = 0
        while True:
             with name_lock:
                  if name:
                       currentName = name[random.randint(0,len(name)-1)]
                       print(f"trading with: {currentName}")
                       pyautogui.moveTo(1400,822)
                       pyautogui.click()
                       pyautogui.moveTo(2250, 1350)
                       pyautogui.click()
                       pyautogui.hotkey('ctrl', 'a')
                       pyautogui.write(currentName)
                       inputNameHasRan = True
                       time.sleep(30)
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
               if numOfTrades % 25 == 0:
                    print(f"{numOfTrades} trades completed.")
                    pyautogui.moveTo(180,1365)
                    pyautogui.click()
                    pyautogui.write(insult[random.randint(0,8)])
                    pyautogui.press('enter')
                    time.sleep(2)
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
