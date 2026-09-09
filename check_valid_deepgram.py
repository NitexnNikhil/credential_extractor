# import csv
# import requests

# INPUT_CSV = "deepgram_data.csv"
# OUTPUT_CSV = "deepgram_keys_checked.csv"


# # def check_deepgram_key(api_key):
# #     url = "https://api.deepgram.com/v1/auth/token"

# #     try:
# #         response = requests.get(
# #             url,
# #             headers={
# #                 "Authorization": f"Token {api_key}",
# #                 "Content-Type": "application/json",
# #             },
# #             timeout=10,
# #         )

# #         if response.status_code == 200:
# #             return "VALID"

# #         if response.status_code == 401:
# #             return "INVALID_KEY"

# #         return f"ERROR_{response.status_code}"

# #     except requests.RequestException:
# #         return "REQUEST_ERROR"

# def check_deepgram_key(api_key):
#     url = "https://api.deepgram.com/v1/auth/token"

#     try:
#         response = requests.get(
#             url,
#             headers={"Authorization": f"Token {api_key}"},
#             timeout=10,
#         )

#         print("STATUS:", response.status_code)
#         print("RESPONSE:", response.text)
#         print("-" * 80)

#         if response.status_code == 200:
#             return "VALID"

#         if response.status_code == 401:
#             return "INVALID_KEY"

#         return f"ERROR_{response.status_code}"

#     except requests.RequestException as e:
#         print("REQUEST ERROR:", e)
#         return "REQUEST_ERROR"


# with open(INPUT_CSV, newline="", encoding="utf-8") as infile:
#     reader = csv.DictReader(infile)

#     rows = []

#     for row in reader:
#         email = row["email"]
#         api_key = row["DEEPGRAM_API_KEY"]

#         status = check_deepgram_key(api_key)

#         print(f"{email} -> {status}")

#         row["STATUS"] = status
#         rows.append(row)


# with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as outfile:
#     fieldnames = [
#         "email",
#         "DEEPGRAM_API_KEY",
#         "PROJECT_ID",
#         "STATUS",
#     ]

#     writer = csv.DictWriter(outfile, fieldnames=fieldnames)
#     writer.writeheader()
#     writer.writerows(rows)

# print(f"\nDone. Output saved to: {OUTPUT_CSV}")





# def check_deepgram_for_livekit(api_key):
#     url = "https://api.deepgram.com/v1/listen"

#     params = {
#         "model": "nova-3",
#         "language": "en-US",
#     }

#     headers = {
#         "Authorization": f"Token {api_key}",
#         "Content-Type": "audio/wav",
#     }

#     # You need a small WAV file here
#     with open("test.wav", "rb") as audio:
#         response = requests.post(
#             url,
#             params=params,
#             headers=headers,
#             data=audio,
#             timeout=30,
#         )

#     print("STATUS:", response.status_code)
#     print("RESPONSE:", response.text[:500])

#     if response.status_code == 200:
#         return "VALID"

#     if response.status_code == 401:
#         return "INVALID_KEY"

#     if response.status_code == 403:
#         return "FORBIDDEN"

#     return f"ERROR_{response.status_code}"



import csv
import requests

INPUT_CSV = "deepgram_data.csv"
OUTPUT_CSV = "deepgram_keys_diagnostic.csv"


def check_auth(api_key):
    """Check whether Deepgram accepts the API key."""
    url = "https://api.deepgram.com/v1/auth/token"

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Token {api_key}"},
            timeout=10,
        )

        return {
            "status_code": response.status_code,
            "response": response.text,
            "valid": response.status_code == 200,
        }

    except requests.RequestException as e:
        return {
            "status_code": None,
            "response": str(e),
            "valid": False,
        }


def check_project(api_key, project_id):
    """Check whether the API key can access the supplied project."""
    url = f"https://api.deepgram.com/v1/projects/{project_id}"

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Token {api_key}"},
            timeout=10,
        )

        return {
            "status_code": response.status_code,
            "response": response.text,
            "valid": response.status_code == 200,
        }

    except requests.RequestException as e:
        return {
            "status_code": None,
            "response": str(e),
            "valid": False,
        }


def check_projects(api_key):
    """Get projects accessible by this API key."""
    url = "https://api.deepgram.com/v1/projects"

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Token {api_key}"},
            timeout=10,
        )

        return {
            "status_code": response.status_code,
            "response": response.text,
        }

    except requests.RequestException as e:
        return {
            "status_code": None,
            "response": str(e),
        }


def diagnose(api_key, project_id):
    auth = check_auth(api_key)

    # If authentication itself fails, don't continue with project checks.
    if not auth["valid"]:
        return {
            "AUTH_STATUS": f"FAILED_{auth['status_code']}",
            "AUTH_RESPONSE": auth["response"],
            "PROJECT_STATUS": "NOT_CHECKED",
            "PROJECT_RESPONSE": "",
            "PROJECTS_STATUS": "NOT_CHECKED",
            "DIAGNOSIS": "API_KEY_INVALID_OR_REVOKED",
        }

    project = check_project(api_key, project_id)
    projects = check_projects(api_key)

    if project["valid"]:
        diagnosis = "VALID_KEY_AND_PROJECT_ACCESS"
    elif project["status_code"] == 403:
        diagnosis = "VALID_KEY_BUT_NO_PROJECT_PERMISSION"
    elif project["status_code"] == 404:
        diagnosis = "VALID_KEY_BUT_PROJECT_NOT_FOUND"
    else:
        diagnosis = f"VALID_KEY_PROJECT_CHECK_{project['status_code']}"

    return {
        "AUTH_STATUS": f"OK_{auth['status_code']}",
        "AUTH_RESPONSE": auth["response"],
        "PROJECT_STATUS": f"{project['status_code']}",
        "PROJECT_RESPONSE": project["response"],
        "PROJECTS_STATUS": f"{projects['status_code']}",
        "DIAGNOSIS": diagnosis,
    }


def main():
    with open(INPUT_CSV, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        rows = []

        for row in reader:
            email = row["email"]
            api_key = row["DEEPGRAM_API_KEY"]
            project_id = row["PROJECT_ID"]

            print(f"\nChecking: {email}")

            result = diagnose(api_key, project_id)

            print(f"  Auth:       {result['AUTH_STATUS']}")
            print(f"  Project:    {result['PROJECT_STATUS']}")
            print(f"  Projects:   {result['PROJECTS_STATUS']}")
            print(f"  Diagnosis:  {result['DIAGNOSIS']}")

            row.update(result)
            rows.append(row)

    fieldnames = [
        "email",
        "DEEPGRAM_API_KEY",
        "PROJECT_ID",
        "AUTH_STATUS",
        "PROJECT_STATUS",
        "PROJECTS_STATUS",
        "DIAGNOSIS",
        "AUTH_RESPONSE",
        "PROJECT_RESPONSE",
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone.")
    print(f"Output: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()