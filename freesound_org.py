import requests
import os
import json

# Freesound API 기본 설정
CLIENT_ID = "RITfSIf63D26oIRXUfsE"
CLIENT_SECRET = "G2uAKUnd0gZsIX5TrIFFsJcjjqmGmP8WXx3BQV2C"
ACCESS_TOKEN = "jhbuYUt2xaZNPkxceOPiYA3y0tlkdf"
REFRESH_TOKEN = "7jrcGlqPhCgQabT9o2aA60pUgdQYiJ"
BASE_URL = "https://freesound.org/apiv2"

DOWNLOAD_DIR = "freesound_effects"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

DOWNLOADED_IDS_FILE = "downloaded_ids.json"
PROGRESS_FILE = "progress.json"

# JSON 파일 로드 및 저장 유틸리티
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return set(json.load(f))
    return set()

def save_json(data, file_path):
    with open(file_path, "w") as f:
        json.dump(list(data), f)

# Access Token 갱신
def refresh_access_token():
    global ACCESS_TOKEN, REFRESH_TOKEN
    token_url = f"{BASE_URL}/oauth2/access_token/"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        tokens = response.json()
        ACCESS_TOKEN = tokens["access_token"]
        REFRESH_TOKEN = tokens["refresh_token"]
        print("Access token refreshed.")
    else:
        raise Exception("Unable to refresh access token:", response.text)

# 검색 기능 (현재 페이지 범위 처리)
def search_effect_sounds(start_page, end_page, page_size=100):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    results = []

    for page in range(start_page, end_page + 1):
        params = {
            "fields": "id,name,duration,tags,license",
            "page_size": page_size,
            "filter": "license:cc0",
            "page": page,
        }
        response = requests.get(f"{BASE_URL}/search/text/", params=params, headers=headers)

        if response.status_code == 401:  # Unauthorized
            refresh_access_token()
            response = requests.get(f"{BASE_URL}/search/text/", params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            results.extend(data.get("results", []))
            print(f"Page {page} processed.")
        else:
            print(f"Error on page {page}: {response.text}")
            break
    return results

# 음원 다운로드 및 기록 업데이트
def download_sounds(sounds):
    downloaded_ids = load_json(DOWNLOADED_IDS_FILE)

    for sound in sounds:
        sound_id = sound["id"]
        sound_name = sound["name"].replace(" ", "_") + ".mp3"

        if sound_id in downloaded_ids:
            print(f"Sound ID {sound_id} already downloaded. Skipping...")
            continue

        # 다운로드 로직
        endpoint = f"{BASE_URL}/sounds/{sound_id}/download/"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.get(endpoint, headers=headers, stream=True)

        if response.status_code == 200:
            file_path = os.path.join(DOWNLOAD_DIR, sound_name)
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"Downloaded: {file_path}")
            downloaded_ids.add(sound_id)
            save_json(downloaded_ids, DOWNLOADED_IDS_FILE)
        else:
            print(f"Error downloading sound {sound_id}: {response.text}")

# 전체 페이지 범위 관리
def process_pages():
    progress = load_json(PROGRESS_FILE)
    start_page = progress.get("start_page", 1)
    end_page = start_page + 499

    while True:
        print(f"Processing pages {start_page} to {end_page}...")
        sounds = search_effect_sounds(start_page, end_page)
        download_sounds(sounds)

        # 다음 범위로 이동
        start_page = end_page + 1
        end_page = start_page + 499

        save_json({"start_page": start_page}, PROGRESS_FILE)

if __name__ == "__main__":
    process_pages()
