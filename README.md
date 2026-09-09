# Credential Extractor


# ==================================================================================================================================================== #
## 📘 Overview
The **Credential Extractor** project automates the process of **extracting and uploading credentials** for both **LiveKit** and **Deepgram** services.  
It converts raw credential data into structured CSV and JSON formats, and then sends them securely to **Upstash** via API requests.

# ==================================================================================================================================================== #

---

## 📂 Project Structure

| File | Description |
|------|--------------|
| `livekit_extractor.py` | Extracts credentials from `LIVEKIT_KEYS.txt` and saves them to `LIVEKIT_DATA.csv`. |
| `livekit_sender.py` | Sends or removes LiveKit credentials in Upstash using `keyId` lookup from LiveKit JSON files. |
| `deepgram_extractor.py` | Extracts credentials from `DEEPGRAM_KEYS.txt` and saves them to `DEEPGRAM_DATA.csv`. |
| `deepgram_sender.py` | Sends or removes Deepgram credentials in Upstash using `keyId` lookup from a Deepgram JSON file. |
| `LIVEKIT_KEYS.txt` | Contains raw LiveKit credentials (Email, URL, API Key, Secret). |
| `DEEPGRAM_KEYS.txt` | Contains raw Deepgram credentials (Email, API Key). |
| `extracted_data.csv` | Stores published and verified credentials. |

# Note -> | `extracted2_data copy.csv` | Contains credentials ready to be sent to Upstash. |


# ==================================================================================================================================================== #

---

## ⚙️ How It Works

### 🔹 LiveKit Credentials Extraction

1. Run the extractor to parse credentials from `LIVEKIT_KEYS.txt`:
    ```bash
    python livekit_extractor.py
    ```
    - Output: `LIVEKIT_DATA.csv` (rewritten if it already exists)
    - Note: The extracted data is structured and ready for sending.

2. Send the extracted credentials to Upstash:
    ```bash
    python livekit_sender.py
    ```
    - Converts CSV → JSON (format: `email, LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET`)
    - Sends securely via Upstash API endpoint.

3. Remove LiveKit credentials from Upstash:
    ```bash
    python3 livekit_sender.py --remove --provider livekit-hotfix
    ```
    - Reads the CSV, matches each row against `src/livekit-hotfix.json` or `src/livekit.json`
    - Extracts the matching `keyId`
    - Sends `{ "provider": "...", "keyId": "..." }` to `https://fleet.aceint.ai/key/delete`
    - Use `--provider livekit` to match against `src/livekit.json`


# ==================================================================================================================================================== #

---

### 🔹 Deepgram Credentials Extraction

1. Run the extractor to parse credentials from `DEEPGRAM_KEYS.txt`:
    ```bash
    python deepgram_extractor.py
    ```
    - Output: `DEEPGRAM_DATA.csv` (rewritten if it already exists)

2. Send the extracted credentials to Upstash:
    ```bash
    python deepgram_sender.py
    ```
    - Converts CSV → JSON (format: `email, DEEPGRAM_API_KEY`)
    - Sends securely via Upstash API endpoint.
    - Optional: choose the payload provider with `--provider`
      ```bash
      python deepgram_sender.py --provider deepgram-hotfix
      python deepgram_sender.py --provider deepgram
      ```

3. Remove Deepgram credentials from Upstash:
    ```bash
    python3 deepgram_sender.py --remove --provider deepgram-hotfix --keys-json /path/to/deepgram.json
    ```
    - Reads the CSV, matches each row against the Deepgram JSON file
    - Extracts the matching `keyId`
    - Sends `{ "provider": "...", "keyId": "..." }` to `https://fleet.aceint.ai/key/delete`
    - Use `--provider deepgram` if your JSON file uses the plain `deepgram` provider

---

# ==================================================================================================================================================== #

## 🧠 Notes

- Ensure `LIVEKIT_KEYS.txt` and `DEEPGRAM_KEYS.txt` exist before running extractors.
- The extractor overwrites existing CSV files if present.
- The sender scripts automatically skip duplicates during upload.
- Remove mode uses `keyId` matching from the corresponding JSON file before calling the delete endpoint.
- `.env` file should include API endpoint and authentication tokens for secure data transfer.

---

# ==================================================================================================================================================== #

## ✅ Example Output Format

### LiveKit JSON Example:
```json
[
  {
    "email": "user@example.com",
    "LIVEKIT_URL": "wss://example.livekit.cloud",
    "LIVEKIT_API_KEY": "abcd1234",
    "LIVEKIT_API_SECRET": "efgh5678"
  }
]
```

LiveKit JSON files used for delete lookup:
- `src/livekit.json`
- `src/livekit-hotfix.json`

### Deepgram JSON Example:
```json
[
  {
    "email": "user@example.com",
    "DEEPGRAM_API_KEY": "xyz9876"
  }
]
```

For Deepgram delete lookup, pass the JSON file path with `--keys-json`.

---

## 🧩 Dependencies

Make sure you have the following installed:

```bash
pip install requests python-dotenv pandas
```

---

## 🏁 Execution Order Summary

1️⃣ **LiveKit**  
  - `python livekit_extractor.py`  
  - `python livekit_sender.py`  
  - `python3 livekit_sender.py --remove --provider livekit-hotfix`

2️⃣ **Deepgram**  
  - `python deepgram_extractor.py`  
  - `python deepgram_sender.py`  
  - `python3 deepgram_sender.py --remove --provider deepgram-hotfix --keys-json /path/to/deepgram.json`

---

## 📜 License
This project is licensed for internal use only. Redistribution or commercial use requires prior authorization.

# ==================================================================================================================================================== #
