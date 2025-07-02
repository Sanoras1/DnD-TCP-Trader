# DnD-TCP-Trader

This repository contains various Python scripts for automating trading actions in the game **Dark and Darker**. The tools were created to help combat trade spammers by automating repetitive UI interactions and monitoring network packets.

## Dependencies

Python 3.11 or later is recommended. Install the required packages using `requirements.txt`:

```bash
pip install -r requirements.txt
```

These scripts also rely on the system installation of [Tesseract OCR](https://github.com/tesseract-ocr/tesseract). Most scripts assume a Windows environment, though Docker support is provided for Linux via WSL.

## Usage

Run the main trade spamming script:

```bash
python Main/tradeSpamSpammersDnD.py
```

Other networking examples such as the fake handshake tool can be launched in a similar way:

```bash
python Main/TCP_fake_handshake_connection.py
```

Image resources used by the automation scripts are stored in the `assets` directory. If you modify or replace any of the PNG files, keep the filenames the same so the scripts continue to locate them.
# tradeSpamSpammersDnD
This project contains several experiments for automating actions in the game
**Dark and Darker**. Use responsibly and at your own risk. Automating gameplay
may violate the game's terms of service.


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

## License

This project is licensed under the [MIT License](LICENSE).
