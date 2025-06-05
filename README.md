# Dark and Darker Sans Toolkit

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
