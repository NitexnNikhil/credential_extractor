import csv
import email
import requests
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API_URL = "https://vtvrzei86g.execute-api.ap-south-1.amazonaws.com/prod/key/add"
API_URL = "https://fleet.aceint.ai/key/add"

CSV_FILE = "/Users/nikhilpathrabe/Documents/Projects/bootcoding/extrator_csv/extracted2_data copy.csv"

HEADERS = {
    "Content-Type": "application/json"
}

# ---------------------------
# Read CSV and build payloads
# ---------------------------
all_payloads = []

with open(CSV_FILE, mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        payload = {
            "provider": "livekit",
            "metadata": {
                "email": row.get("email", "").strip(),
                "LIVEKIT_URL": row.get("LIVE_KIT_URL", "").strip(),
                "LIVEKIT_API_KEY": row.get("LIVEKIT_API_KEYS", "").strip(),
                "LIVEKIT_API_SECRET": row.get("LIVEKIT_SECRET_KEYS", "").strip()
            }
        }
        all_payloads.append(payload)

print(f"✅ Collected {len(all_payloads)} credentials from CSV")

# ---------------------------
# Send each credential one-by-one
# ---------------------------
success_count = 0
failure_count = 0

for idx, payload in enumerate(all_payloads, start=1):
    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=15)

        if response.status_code == 200 or response.status_code == 201:
            success_count += 1
            print(f"✅ [{idx}/{len(all_payloads)}] Sent successfully for: {payload['metadata']['email']}")
            print(response.status_code, email)
        else:
            failure_count += 1
            print(f"❌ [{idx}/{len(all_payloads)}] Failed ({response.status_code}): {response.text}")

        # optional delay to avoid rate limiting
        time.sleep(0.5)

    except Exception as e:
        failure_count += 1
        print(f"⚠️ [{idx}/{len(all_payloads)}] Error sending data for {payload['metadata']['email']}: {e}")

print("\n📊 Summary:")
print(f"   ✅ Success: {success_count}")
print(f"   ❌ Failed:  {failure_count}")
