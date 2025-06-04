import pyautogui
import threading
import time
import random
from findNames import name
#https://github.com/Sanoras1/tradeSpamSpammersDnD/tree/main

pyautogui.FAILSAFE = True
name_lock = threading.Lock()
beginFindName = True
inputNameHasRan = False
screenshotList = []
screenshotCreate5HasRan = False

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
thread3 = threading.Thread(target=spamTrader, daemon=True)
thread3.start()

while True:
    time.sleep(1)