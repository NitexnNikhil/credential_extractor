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

# API_URL = "https://vtvrzei86g.execute-api.ap-south-1.amazonaws.com/prod/key/add"
ADD_API_URL = "https://fleet.aceint.ai/key/add"
DELETE_API_URL = "https://fleet.aceint.ai/key/delete"

CSV_FILE = "/Users/nikhilpathrabe/Documents/Projects/bootcoding/extrator_csv/extracted2_data copy.csv"
JSON_FILES = {
    "livekit": "/Users/nikhilpathrabe/Documents/Projects/bootcoding/extrator_csv/src/livekit.json",
    "livekit-hotfix": "/Users/nikhilpathrabe/Documents/Projects/bootcoding/extrator_csv/src/livekit-hotfix.json",
}

HEADERS = {
    "Content-Type": "application/json"
}

def resolve_provider(provider_arg: str | None) -> str:
    """
    Map CLI aliases to the provider value sent in the payload.
    """
    if not provider_arg:
        return "livekit-hotfix"

    provider_aliases = {
        "livekit": "livekit",
        "livekit-hotfix": "livekit-hotfix",
        "lk": "livekit",
        "lk-hotfix": "livekit-hotfix",
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
    url_value = row.get("LIVE_KIT_URL", "").strip()
    api_key_value = row.get("LIVEKIT_API_KEYS", "").strip()
    secret_value = row.get("LIVEKIT_SECRET_KEYS", "").strip()

    for key_id, record in key_index.items():
        if email_value and record.get("email", "").strip().lower() != email_value:
            continue
        if url_value and record.get("LIVEKIT_URL", "").strip() != url_value:
            continue
        if api_key_value and record.get("LIVEKIT_API_KEY", "").strip() != api_key_value:
            continue
        if secret_value and record.get("LIVEKIT_API_SECRET", "").strip() != secret_value:
            continue
        return record.get("id", key_id)

    return None

parser = argparse.ArgumentParser(description="Send LiveKit credentials to Upstash")
parser.add_argument(
    "--remove",
    action="store_true",
    help="Remove LiveKit credentials instead of adding them",
)
parser.add_argument(
    "--provider",
    default="livekit-hotfix",
    help="Provider name to send in payload metadata (default: livekit-hotfix)",
)
args = parser.parse_args()
provider = resolve_provider(args.provider)
api_url = DELETE_API_URL if args.remove else ADD_API_URL
action_verb = "Removed" if args.remove else "Sent"
json_file = JSON_FILES.get(provider, JSON_FILES["livekit-hotfix"])

# ---------------------------
# Read CSV and build payloads
# ---------------------------
all_payloads = []
key_index = load_key_index(json_file) if args.remove else {}

with open(CSV_FILE, mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        key_id = None
        if args.remove:
            key_id = find_matching_key_id(row, key_index)
            if not key_id:
                print(
                    f"⚠️ Skipping row for {row.get('email', '').strip()} because no matching keyId was found in {Path(json_file).name}"
                )
                continue

        payload = {
            "provider": provider,
            "metadata": {
                "email": row.get("email", "").strip(),
                "LIVEKIT_URL": row.get("LIVE_KIT_URL", "").strip(),
                "LIVEKIT_API_KEY": row.get("LIVEKIT_API_KEYS", "").strip(),
                "LIVEKIT_API_SECRET": row.get("LIVEKIT_SECRET_KEYS", "").strip()
            }
        }
        if args.remove:
            payload = {
                "provider": provider,
                "keyId": key_id,
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
        if args.remove:
            response = requests.post(api_url, json=payload, headers=HEADERS, timeout=15)
        else:
            response = requests.post(api_url, json=payload, headers=HEADERS, timeout=15)

        if response.status_code in (200, 201, 204):
            success_count += 1
            if args.remove:
                print(f"✅ [{idx}/{len(all_payloads)}] Removed successfully for keyId: {payload['keyId']}")
            else:
                print(f"✅ [{idx}/{len(all_payloads)}] Sent successfully for: {payload['metadata']['email']}")
            print(response.status_code, payload.get("keyId", payload["metadata"]["email"]))
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
