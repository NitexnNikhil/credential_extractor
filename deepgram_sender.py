# |--------------------------------------------------------------|#
# | NOW onwards ✅ Send All 50+ Credentials in One JSON Payload. |
# |--------------------------------------------------------------|#
import csv
import email
import argparse
import requests
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CSV_FILE = "deepgram_data.csv"
ADD_API_URL = "https://fleet.aceint.ai/key/add"
DELETE_API_URL = "https://fleet.aceint.ai/key/delete"

HEADERS = {
    "Content-Type": "application/json"
}

def resolve_provider(provider_arg: str | None) -> str:
    """
    Map CLI aliases to the provider value sent in the payload.
    """
    if not provider_arg:
        return "deepgram-hotfix"

    provider_aliases = {
        "deepgram": "deepgram",
        "deepgram-hotfix": "deepgram-hotfix",
        "dg": "deepgram",
        "dg-hotfix": "deepgram-hotfix",
    }

    normalized = provider_arg.strip().lower()
    return provider_aliases.get(normalized, provider_arg.strip())


def load_key_index(json_path: str) -> dict[str, dict]:
    with open(json_path, mode="r", encoding="utf-8") as file:
        data = json.load(file)

    response = data.get("response", {})
    index = {}
    for key_id, record in response.items():
        if isinstance(record, dict) and key_id.startswith("key_"):
            index[key_id] = record
    return index


def find_matching_key_id(row: dict, key_index: dict[str, dict]) -> str | None:
    email_value = row.get("email", "").strip().lower()
    project_id_value = row.get("PROJECT_ID", "").strip()
    api_key_value = row.get("DEEPGRAM_API_KEY", "").strip()

    for key_id, record in key_index.items():
        if email_value and record.get("email", "").strip().lower() != email_value:
            continue
        if project_id_value and record.get("PROJECT_ID", "").strip() != project_id_value:
            continue
        if api_key_value and record.get("DEEPGRAM_API_KEY", "").strip() != api_key_value:
            continue
        return record.get("id", key_id)

    return None

parser = argparse.ArgumentParser(description="Send Deepgram credentials to Upstash")
parser.add_argument(
    "--remove",
    action="store_true",
    help="Remove Deepgram credentials instead of adding them",
)
parser.add_argument(
    "--provider",
    default="deepgram-hotfix",
    help="Provider name to send in payload metadata (default: deepgram-hotfix)",
)
parser.add_argument(
    "--keys-json",
    default="deepgram.json",
    help="Path to the Deepgram JSON file used to resolve keyId during removal",
)
args = parser.parse_args()
provider = resolve_provider(args.provider)
api_url = DELETE_API_URL if args.remove else ADD_API_URL
json_file = args.keys_json

# ---------------------------
# Read CSV and build payloads
# ---------------------------
all_payloads = []
key_index = load_key_index(json_file) if args.remove else {}

with open(CSV_FILE, mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        if args.remove:
            key_id = find_matching_key_id(row, key_index)
            if not key_id:
                print(
                    f"⚠️ Skipping row for {row.get('email', '').strip()} because no matching keyId was found in {Path(json_file).name}"
                )
                continue
            payload = {
                "provider": provider,
                "keyId": key_id,
            }
        else:
            payload = {
                "provider": provider,
                "metadata": {
                    "email": row.get("email", "").strip(),
                    "PROJECT_ID": row.get("PROJECT_ID", "").strip(),
                    "DEEPGRAM_API_KEY": row.get("DEEPGRAM_API_KEY", "").strip(),
                    "maxConcurrency": 15, # Override default concurrency for this key to 15 for Deepgram
                }
            }
        all_payloads.append(payload)
        
print("✅ Collected", len(all_payloads), "credentials from CSV")

# ---------------------------
# Send each credential one-by-one
# ---------------------------

success_count = 0
failure_count = 0

for idx, payload in enumerate(all_payloads, start=1):
    try:
        if args.remove:
            response = requests.post(api_url, json=payload, headers=HEADERS, timeout=15)
        else:
            response = requests.post(api_url, json=payload, headers=HEADERS, timeout=15)

        if response.status_code in (200, 201, 204):
            success_count += 1
            if args.remove:
                print(f"✅ [{idx}/{len(all_payloads)}] Removed successfully for keyId: {payload['keyId']}")
                print(response.status_code, payload["keyId"])
            else:
                print(f"✅ [{idx}/{len(all_payloads)}] Sent successfully for: {payload['metadata']['email']}")
                # print(response.status_code, email)
                print(response.status_code, payload['metadata']['email'])
        else:
            failure_count += 1
            print(f"❌ [{idx}/{len(all_payloads)}] Failed ({response.status_code}): {response.text}")

        # optional delay to avoid rate limiting
        time.sleep(0.5)

    except Exception as e:
        failure_count += 1
        if args.remove:
            print(f"⚠️ [{idx}/{len(all_payloads)}] Error removing keyId {payload['keyId']}: {e}")
        else:
            print(f"⚠️ [{idx}/{len(all_payloads)}] Error sending data for {payload['metadata']['email']}: {e}")

print("\n📊 Summary:")
print(f"   ✅ Success: {success_count}")
print(f"   ❌ Failed:  {failure_count}")
