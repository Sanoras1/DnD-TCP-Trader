# tradeSpamSpammersDnD
This project contains several experiments for automating actions in the game
**Dark and Darker**. Use responsibly and at your own risk. Automating gameplay
may violate the game's terms of service.

Requirements to run:
1. pyautogui (pip install pyautogui)
2. pytesseract (pip install pytesseract) this is just a python wrapper for tesseract ocr.
3. tesseract OCR
4. requires Windows operating system
5. not required, but utilizes docker
6. if using Docker make note to use a Linux based OS. On Windows you can use services such as **WSL**.

Install the dependencies with:
```bash
pip install -r requirements.txt
```

Image resources used by the automation scripts are stored in the `assets`
directory at the repository root. If you modify or replace any of the PNG
files make sure to keep the same filenames as referenced in the code.
