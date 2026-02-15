import requests
import os

url = "http://127.0.0.1:8000/search/"
file_path = r"c:\xampp\htdocs\empreintes\backend\images\fvc\DB1_B\101_1.tif"

if not os.path.exists(file_path):
    print(f"❌ File not found: {file_path}")
else:
    print(f"Testing search API with {file_path}...")
    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "image/tiff")}
            response = requests.post(url, files=files, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
