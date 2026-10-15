import asyncio
import csv
from typing import Dict, List

from livekit import api
from websockets.asyncio.client import connect


INPUT_CSV = "credentials.csv"
OUTPUT_CSV = "working_credentials.csv"

# Columns expected in input CSV
FIELD_EMAIL = "email"
FIELD_URL = "LIVE_KIT_URL"
FIELD_API_KEY = "LIVEKIT_API_KEYS"
FIELD_API_SECRET = "LIVEKIT_SECRET_KEYS"


def build_wss_url(base_url: str, token: str) -> str:
    """
    Normalize LIVE_KIT_URL and build final WSS URL for /rtc with access_token.
    Accepts:
      - voice17-xxxx.livekit.cloud
      - https://voice17-xxxx.livekit.cloud
      - wss://voice17-xxxx.livekit.cloud
      - wss://voice17-xxxx.livekit.cloud/rtc
    Returns:
      wss://host/rtc?access_token=...
    """
    url = base_url.strip()

    # Strip scheme if https:// is used and switch to wss://
    if url.startswith("https://"):
        url = "wss://" + url[len("https://") :]
    # Add wss:// if no scheme is present
    elif not url.startswith("wss://"):
        url = "wss://" + url

    # Ensure /rtc path exists
    if "/rtc" not in url:
        if url.endswith("/"):
            url = url[:-1]
        url = url + "/rtc"

    # Append token
    return f"{url}?access_token={token}"


def generate_room_token(
    api_key: str,
    api_secret: str,
    identity: str = "health-check",
    room: str = "health-check-room",
) -> str:
    """
    Generate a LiveKit JWT token with room_join grants.
    """
    token = (
        api.AccessToken(api_key, api_secret)
        .with_identity(identity)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
            )
        )
    )
    return token.to_jwt()


async def test_single_credential(row: Dict[str, str]) -> bool:
    """
    For a single CSV row:
      - Generate token
      - Try WSS connection
    Return True if considered valid, False otherwise.
    """
    email = row.get(FIELD_EMAIL, "").strip()
    base_url = row.get(FIELD_URL, "").strip()
    api_key = row.get(FIELD_API_KEY, "").strip()
    api_secret = row.get(FIELD_API_SECRET, "").strip()

    if not (base_url and api_key and api_secret):
        print(f"[SKIP] Missing fields for email={email}")
        return False

    try:
        token = generate_room_token(api_key, api_secret)
    except Exception as e:
        print(f"[INVALID TOKEN] email={email}, url={base_url}: {e}")
        return False

    wss_url = build_wss_url(base_url, token)

    try:
        # You can tweak timeouts as needed
        async with connect(wss_url, open_timeout=5, close_timeout=5) as ws:
            print(f"[OK] Connected: email={email}, url={base_url}")
            await ws.close()
            return True
    except Exception as e:
        # This is where failures get logged
        print(f"[FAIL] email={email}, url={base_url}: {e}")
        return False


async def process_all_credentials(input_csv: str, output_csv: str) -> None:
    """
    Read all credentials from input_csv,
    test each, and write valid & failed ones to separate CSVs.
    """
    valid_rows: List[Dict[str, str]] = []
    failed_rows: List[Dict[str, str]] = []

    # Read input CSV
    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} credential rows from {input_csv}")

    # Test each row sequentially (simpler & safer for rate limits).
    for idx, row in enumerate(rows, start=1):
        email = row.get(FIELD_EMAIL, "").strip()
        print(f"\n[{idx}/{len(rows)}] Testing email={email}...")
        is_valid = await test_single_credential(row)
        if is_valid:
            valid_rows.append(row)
        else:
            failed_rows.append(row)

    # -----------------------------
    # WRITE WORKING CREDENTIALS CSV
    # -----------------------------
    if valid_rows:
        fieldnames = [FIELD_EMAIL, FIELD_URL, FIELD_API_KEY, FIELD_API_SECRET]
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in valid_rows:
                writer.writerow(
                    {
                        FIELD_EMAIL: r.get(FIELD_EMAIL, ""),
                        FIELD_URL: r.get(FIELD_URL, ""),
                        FIELD_API_KEY: r.get(FIELD_API_KEY, ""),
                        FIELD_API_SECRET: r.get(FIELD_API_SECRET, ""),
                    }
                )
        print(f"\n✅ Wrote {len(valid_rows)} working credentials to {output_csv}")
    else:
        print("\n⚠️ No working credentials found. Nothing written.")

    # -----------------------------
    # WRITE FAILED CREDENTIALS CSV
    # -----------------------------
    if failed_rows:
        fieldnames = [FIELD_EMAIL, FIELD_URL, FIELD_API_KEY, FIELD_API_SECRET]
        with open("failed_credentials.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in failed_rows:
                writer.writerow(
                    {
                        FIELD_EMAIL: r.get(FIELD_EMAIL, ""),
                        FIELD_URL: r.get(FIELD_URL, ""),
                        FIELD_API_KEY: r.get(FIELD_API_KEY, ""),
                        FIELD_API_SECRET: r.get(FIELD_API_SECRET, ""),
                    }
                )

        print(f"❌ Wrote {len(failed_rows)} failed credentials to failed_credentials.csv")
    else:
        print("\n🟢 No failures! All credentials valid.")


if __name__ == "__main__":
    asyncio.run(process_all_credentials(INPUT_CSV, OUTPUT_CSV))
