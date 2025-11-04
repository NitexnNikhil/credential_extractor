# import csv
# import stat
# import requests
# import os
# import json
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# API_URL = "https://vtvrzei86g.execute-api.ap-south-1.amazonaws.com/prod/key/add"
# CSV_FILE = "extracted2_data copy.csv"

# HEADERS = {
#     "Content-Type": "application/json"
# }

# all_payloads = []

# # ---------------------------
# # Read CSV and build payloads
# # ---------------------------
# with open(CSV_FILE, mode="r", encoding="utf-8") as file:
#     reader = csv.DictReader(file)
#     for row in reader:
#         payload = {
#             "provider": "livekit",
#             "metadata": {
#                 "email": row.get("email", "").strip(),
#                 "LIVEKIT_URL": row.get("LIVE_KIT_URL", "").strip(),
#                 "LIVEKIT_API_KEY": row.get("LIVEKIT_API_KEYS", "").strip(),
#                 "LIVEKIT_API_SECRET": row.get("LIVEKIT_SECRET_KEYS", "").strip()
#             }
#         }
#         all_payloads.append(payload)

# print(f"✅ Collected {len(all_payloads)} credentials from CSV")

# # ---------------------------
# # Send all credentials as one JSON array
# # ---------------------------
# try:
#     # response = requests.post(
#     #     API_URL,
#     #     json={"value": all_payloads},  # send all together
#     #     headers=HEADERS,
#     #     timeout=30
#     # )

#     response = requests.post(
#     API_URL,
#     json=all_payloads[0],
#     headers=HEADERS,
#     timeout=30
#     )


#     print(f"✅ Sent {len(all_payloads)} credentials in one request")
#     print(f"Status: {response.status_code}")
#     print(f"Response: {response.text}")

#     if response.status_code != 200 :
#         print("⚠️ Something went wrong. Check the response above.")

# except Exception as e:
#     print("❌ Error sending data:", e)



import csv
import email
import requests
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = "https://vtvrzei86g.execute-api.ap-south-1.amazonaws.com/prod/key/add"
CSV_FILE = "extracted2_data copy.csv"

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
