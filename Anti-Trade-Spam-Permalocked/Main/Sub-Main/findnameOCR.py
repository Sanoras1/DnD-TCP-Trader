import pyautogui
import time
import pytesseract
from PIL import Image
import threading

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pyautogui.FAILSAFE = True
name_lock = threading.Lock()
beginFindName = True
name = []
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

thread1 = threading.Thread(target=findName, daemon=True)
thread1.start()

thread2 = threading.Thread(target=screenshotCreate5, daemon=True)
thread2.start()