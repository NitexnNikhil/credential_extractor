
# # |--------------------------------------------------------------|#
# # | NOW onwards ✅ Send IN BATCH OF 5 |
# # |--------------------------------------------------------------|#
# import csv
# import requests
# import time
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
# UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
# KEY = "livekit_credentials_test_batch"

# # Use RPUSH to append multiple objects as a queue
# API_URL = f"{UPSTASH_URL}/rpush/{KEY}"

# CSV_FILE = "extracted_data.csv"
# BATCH_SIZE = 5

# # ✅ Always include authorization
# HEADERS = {
#     "Authorization": f"Bearer {UPSTASH_TOKEN}",
#     "Content-Type": "application/json"
# }

# print("✅ UPSTASH_URL:", UPSTASH_URL)
# print("✅ UPSTASH_TOKEN:", UPSTASH_TOKEN[:8] + "..." if UPSTASH_TOKEN else "⚠️ Missing")

# with open(CSV_FILE, mode='r', encoding='utf-8') as file:
#     reader = csv.DictReader(file)
#     batch = []
#     for row in reader:
#         payload = {
#             "provider": "livekit",
#             "metadata": {
#                 "email": row["email"],
#                 "LIVEKIT_URL": row["LIVE_KIT_URL"],
#                 "LIVEKIT_API_KEY": row["LIVEKIT_API_KEYS"],
#                 "LIVEKIT_API_SECRET": row["LIVEKIT_SECRET_KEYS"]
#             }
#         }
#         batch.append(payload)

#         if len(batch) == BATCH_SIZE:
#             response = requests.post(API_URL, json=batch, headers=HEADERS)
#             print(f"✅ Sent batch of {BATCH_SIZE} payloads -> Status: {response.status_code}")
#             print(response.text)
#             print(API_URL)
#             batch = []
#             time.sleep(1)

#     if batch:
#         response = requests.post(API_URL, json=batch, headers=HEADERS)
#         print(f"✅ Sent final batch of {len(batch)} payloads -> Status: {response.status_code}")
#         print(response.text)



# |--------------------------------------------------------------|#
# | NOW onwards ✅ Send IN BATCH OF 5 |
# |--------------------------------------------------------------|#
import csv
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
BASE_KEY = "livekit_credentials_test_batch"
CSV_FILE = "extracted_data.csv"
BATCH_SIZE = 5

HEADERS = {
    "Authorization": f"Bearer {UPSTASH_TOKEN}",
    "Content-Type": "application/json"
}

print("✅ UPSTASH_URL:", UPSTASH_URL)
print("✅ UPSTASH_TOKEN:", UPSTASH_TOKEN[:8] + "..." if UPSTASH_TOKEN else "⚠️ Missing")

with open(CSV_FILE, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    batch = []
    batch_number = 1  # ✅ Start from 1 instead of 0

    for row in reader:
        payload = {
            "provider": "livekit",
            "metadata": {
                "email": row["email"],
                "LIVEKIT_URL": row["LIVE_KIT_URL"],
                "LIVEKIT_API_KEY": row["LIVEKIT_API_KEYS"],
                "LIVEKIT_API_SECRET": row["LIVEKIT_SECRET_KEYS"]
            }
        }
        batch.append(payload)

        if len(batch) == BATCH_SIZE:
            key = f"{BASE_KEY}:{batch_number}"  # ✅ Unique key per batch
            api_url = f"{UPSTASH_URL}/set/{key}"
            response = requests.post(api_url, json=batch, headers=HEADERS)
            print(f"✅ Sent batch {batch_number} -> Status: {response.status_code}")
            print(response.text)
            batch = []
            batch_number += 1
            time.sleep(1)

    if batch:
        key = f"{BASE_KEY}:{batch_number}"
        api_url = f"{UPSTASH_URL}/set/{key}"
        response = requests.post(api_url, json=batch, headers=HEADERS)
        print(f"✅ Sent final batch {batch_number} -> Status: {response.status_code}")
        print(response.text)
