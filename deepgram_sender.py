
# |--------------------------------------------------------------|#
# | NOW onwards ✅ Send All 50+ Credentials in One JSON Payload. |
# |--------------------------------------------------------------|#
import csv
import requests
import os
from dotenv import load_dotenv
import deepgram_extractor

# Load environment variables
load_dotenv()

UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
KEY = "deepgram_credentials_test"

# Using /set to store all credentials as one full JSON array
API_URL = f"{UPSTASH_URL}/set/{KEY}"

CSV_FILE = "deepgram_data.csv"

HEADERS = {
    "Authorization": f"Bearer {UPSTASH_TOKEN}",
    "Content-Type": "application/json"
}

print("✅ UPSTASH_URL:", UPSTASH_URL)
print("✅ Using key:", KEY)

# ---------------------------
# Build the unified payload array
# ---------------------------
all_payloads = []

with open(CSV_FILE, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        payload = {
            "provider": "deepgram",
            "metadata": {
                "email": row["email"],
                "PROJECT_ID": row["PROJECT_ID"],
                "DEEPGRAM_API_KEY": row["DEEPGRAM_API_KEY"]
            }
        }
        all_payloads.append(payload)

# ---------------------------
# Send all credentials as one JSON array
# ---------------------------
response = requests.post(
    API_URL,
    json={"value": all_payloads},  # ✅ send list directly, not as a string
    headers=HEADERS
)

print(f"✅ Sent {len(all_payloads)} credentials in one request")
print(f"Status: {response.status_code}")
print(response.text)
