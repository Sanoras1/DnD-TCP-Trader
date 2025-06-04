import requests
data = {"info": "hello from VM1"}
requests.post("http://<VM2_PUBLIC_IP>:5000/receive", json=data)