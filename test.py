import csv
from pathlib import Path

import requests

INPUT_CSV = "deepgram_data.csv"
OUTPUT_CSV = "deepgram_data_checked.csv"
AUTH_URL = "https://api.deepgram.com/v1/auth/token"


def test_deepgram_api_key(api_key: str) -> tuple[bool, str]:
    """Return whether a Deepgram API key is valid and a short status message."""
    if not api_key.strip():
        return False, "EMPTY_KEY"

    try:
        response = requests.get(
            AUTH_URL,
            headers={"Authorization": f"Token {api_key.strip()}"},
            timeout=10,
        )

        if response.status_code == 200:
            return True, "VALID"

        if response.status_code == 401:
            return False, "INVALID_KEY"

        return False, f"ERROR_{response.status_code}"

    except requests.RequestException:
        return False, "REQUEST_ERROR"


def main() -> None:
    input_path = Path(INPUT_CSV)
    if not input_path.exists():
        print(f"Error: {INPUT_CSV} not found.")
        return

    rows = []

    with input_path.open("r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        required_headers = {"email", "DEEPGRAM_API_KEY", "PROJECT_ID"}

        if not required_headers.issubset(set(reader.fieldnames or [])):
            print("Error: CSV headers mismatch.")
            print(f"Found: {reader.fieldnames}")
            print(f"Expected to contain: {required_headers}")
            return

        for row in reader:
            email = row.get("email", "").strip()
            api_key = row.get("DEEPGRAM_API_KEY", "").strip()
            project_id = row.get("PROJECT_ID", "").strip()

            is_valid, status = test_deepgram_api_key(api_key)
            print(f"{email} -> {status}")

            rows.append(
                {
                    "email": email,
                    "DEEPGRAM_API_KEY": api_key,
                    "PROJECT_ID": project_id,
                    "STATUS": status,
                }
            )

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=["email", "DEEPGRAM_API_KEY", "PROJECT_ID", "STATUS"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. Output saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
