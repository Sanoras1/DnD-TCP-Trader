import os
import sys
import requests

url = os.getenv("DESTINATION_URL")
if len(sys.argv) > 1:
    url = sys.argv[1]

if not url:
    raise SystemExit(
        "Usage: DESTINATION_URL=<url> python spinUpVm.py [url]"
    )

data = {"info": "hello from VM1"}
requests.post(url, json=data)
