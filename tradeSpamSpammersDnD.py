import pyautogui
import threading
import time
import pytesseract
import random
#https://github.com/Sanoras1/tradeSpamSpammersDnD/tree/main

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pyautogui.FAILSAFE = True
name_lock = threading.Lock()
beginFindName = True
name = []
inputNameHasRan = False
 
def findName():
    global beginFindName
    global name
    while beginFindName == True:
        screenShot = pyautogui.screenshot()
        screenShot = screenShot.crop(box=[1000,565,1550,865])
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
     insult = ["stinky", "u suk", "im goonin rn", "im wastin your time bub", "rent free big dawg...", "fortnite balls", "you like cd's? Cee Dee's nuts",
               "when u trading...", "<3 I like to trade you :)"]
     while True:
          if inputNameHasRan:
               pyautogui.moveTo(2155,353)
               pyautogui.rightClick()
               pyautogui.moveTo(2210,400)
               pyautogui.click()
               print("spamming")
               numOfTrades = numOfTrades + 1
               if numOfTrades % 50 == 0:
                    print(f"{numOfTrades} trades completed.")
                    pyautogui.moveTo(180,1365)
                    pyautogui.click()
                    pyautogui.write(insult[random.randint(0,9)])
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

while True:
    time.sleep(1)

