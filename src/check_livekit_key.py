import asyncio
import csv
import os
from livekit import api
from livekit.api import ListRoomsRequest

# --- CONFIGURATION ---
INPUT_CSV = 'livekit_credentials.csv'  # Ensure your file is named this
OUTPUT_CSV = 'unworkable_key.csv'      # The file to generate

async def check_credential(url, api_key, api_secret):
    """
    Attempts to list rooms to verify if credentials are valid.
    Returns True if workable, False if not.
    """
    # specific check for empty values before calling API
    if not url or not api_key or not api_secret:
        return False

    lkapi = api.LiveKitAPI(
        url=url,
        api_key=api_key,
        api_secret=api_secret,
    )

    try:
        # We try to perform a simple read operation (List Rooms)
        await lkapi.room.list_rooms(ListRoomsRequest())
        print(f"✅ Success: {api_key[:6]}... (URL: {url})")
        return True
    
    except Exception as e:
        print(f"❌ Failed: {api_key[:6]}... Error: {e}")
        return False
    
    finally:
        await lkapi.aclose()

async def main():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        return

    unworkable_rows = []
    
    print(f"Reading credentials from {INPUT_CSV}...")
    
    with open(INPUT_CSV, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        
        # Verify headers match your specific format
        required_headers = {'email', 'LIVE_KIT_URL', 'LIVEKIT_API_KEYS', 'LIVEKIT_SECRET_KEYS'}
        
        # simple check to see if our required headers exist in the file
        if not required_headers.issubset(reader.fieldnames):
            print(f"Error: CSV headers mismatch.")
            print(f"Found: {reader.fieldnames}")
            print(f"Expected to contain: {required_headers}")
            return

        tasks = []
        rows = list(reader) 

        for row in rows:
            # map your specific CSV columns to variables
            url = row.get('LIVE_KIT_URL', '').strip()
            key = row.get('LIVEKIT_API_KEYS', '').strip()
            secret = row.get('LIVEKIT_SECRET_KEYS', '').strip()
            
            tasks.append(check_credential(url, key, secret))

        # Run checks concurrently
        results = await asyncio.gather(*tasks)

        # Collect failed rows
        for i, is_working in enumerate(results):
            if not is_working:
                unworkable_rows.append(rows[i])

    # Write unworkable keys to output CSV
    if unworkable_rows:
        print(f"\nWriting {len(unworkable_rows)} unworkable credentials to {OUTPUT_CSV}...")
        with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as outfile:
            # We keep the exact same headers as the input
            fieldnames = ['email', 'LIVE_KIT_URL', 'LIVEKIT_API_KEYS', 'LIVEKIT_SECRET_KEYS']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in unworkable_rows:
                writer.writerow({
                    'email': row['email'],
                    'LIVE_KIT_URL': row['LIVE_KIT_URL'],
                    'LIVEKIT_API_KEYS': row['LIVEKIT_API_KEYS'],
                    'LIVEKIT_SECRET_KEYS': row['LIVEKIT_SECRET_KEYS']
                })
        print("Done.")
    else:
        print("\nAll credentials in the CSV are valid! No output file created.")

if __name__ == "__main__":
    asyncio.run(main())