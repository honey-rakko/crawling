import requests
import os
import json

# Freesound API 기본 설정
CLIENT_ID = "4dDr1nZcw2ZUBe1eYvwE"
CLIENT_SECRET = "DYBhG9A1CTFdhTkKNidyKYkSftxLvUM1mScbmz3O"
ACCESS_TOKEN = "C3Cgiv057zvOhDKnp4nGFHbjSkYBMy"
REFRESH_TOKEN = "A3q7ZDEfsJTUUIHUkHCyajrRL9gb0J"
BASE_URL = "https://freesound.org/apiv2"
METADATA_FILE = "metadata.json"

DOWNLOAD_DIR = "freesound_effects"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

DOWNLOADED_IDS_FILE = "downloaded_ids.json"
PROGRESS_FILE = "progress.json"

# JSON 파일 로드 및 저장 유틸리티
def load_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                # progress.json은 딕셔너리 반환
                if file_path == PROGRESS_FILE:
                    return data  # 딕셔너리 반환
                return set(data)  # 다른 파일은 set으로 반환
        except json.JSONDecodeError:
            print(f"Error: {file_path} is empty or corrupted. Initializing with default values.")
            if file_path == PROGRESS_FILE:
                return {"start_page": 1}  # progress.json 기본값
            return set()  # 다른 파일 기본값
    # 파일이 없을 경우 기본값 반환
    if file_path == PROGRESS_FILE:
        return {"start_page": 1}  # progress.json 기본값
    return set()  # 다른 파일 기본값



def save_json(data, file_path):
    with open(file_path, "w") as f:
        if isinstance(data, set):
            json.dump(list(data), f)  # set은 list로 저장
        else:
            json.dump(data, f)  # dict는 그대로 저장


# Access Token 갱신 함수 수정
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
    global ACCESS_TOKEN
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    results = []

    for page in range(start_page, end_page + 1):
        params = {
            "fields": "id,name,duration,tags,license,avg_rating,num_downloads",  # 필드 확장
            "page_size": page_size,
            "filter": "(tag:effect OR tag:fx OR tag:impact OR tag:foley)",
            "sort": "downloads",  # 다운로드 수 기준 정렬
            "page": page,
        }

        for attempt in range(3):
            response = requests.get(f"{BASE_URL}/search/text/", params=params, headers=headers)

            if response.status_code == 401:  # Unauthorized
                refresh_access_token()
                headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
            elif response.status_code == 200:
                data = response.json()
                results.extend(data.get("results", []))
                print(f"Page {page} processed. Found {len(data.get('results', []))} sounds.")
                break
            else:
                print(f"Error on page {page}, attempt {attempt + 1}: {response.text}")
                if attempt == 2:
                    raise Exception(f"Failed to process page {page} after 3 attempts.")

    print(f"Total sounds found: {len(results)}")
    return results

def save_metadata(metadata, file_path=METADATA_FILE):
    # 기존 메타데이터 로드
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            print(f"Error: {file_path} is empty or corrupted. Reinitializing.")
            existing_data = []
    else:
        existing_data = []

    # 새로운 메타데이터 추가
    existing_data.extend(metadata)

    # 메타데이터 저장
    with open(file_path, "w") as f:
        json.dump(existing_data, f, indent=4)

    print(f"Metadata saved to {file_path}. Total records: {len(existing_data)}")




# 음원 다운로드 및 기록 업데이트
def download_sounds(sounds):
    downloaded_ids = load_json(DOWNLOADED_IDS_FILE)
    print(f"Already downloaded IDs: {len(downloaded_ids)}")

    for sound in sounds:
        sound_id = sound["id"]
        sound_name = sound["name"].replace(" ", "_") + ".mp3"

        if sound_id in downloaded_ids:
            print(f"Sound ID {sound_id} already downloaded. Skipping...")
            continue

        print(f"Downloading sound ID {sound_id} - {sound_name}...")
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

            # 다운로드 성공 시 메타데이터 기록
            metadata = {
                "id": sound_id,
                "name": sound["name"],
                "duration": sound["duration"],
                "tags": sound["tags"],
                "license": sound["license"],
                "avg_rating": sound.get("avg_rating", 0.0),  # 평점 (없으면 0.0)
                "num_downloads": sound.get("num_downloads", 0),  # 다운로드 수 (없으면 0)
                "file_path": file_path,
            }
            save_metadata([metadata])  # 개별적으로 메타데이터 저장
            print(f"Metadata saved for sound ID {sound_id}.")
        else:
            print(f"Error downloading sound {sound_id}: {response.text}")





# 전체 페이지 범위 관리
def process_pages():
    progress = load_json(PROGRESS_FILE)
    start_page = progress.get("start_page", 1)
    end_page = min(start_page + 2, 3)  # 3페이지까지만 처리

    while start_page <= 3:  # 최대 3페이지까지만 실행
        print(f"Processing pages {start_page} to {end_page}...")
        sounds = search_effect_sounds(start_page, end_page)
        print(f"Sounds retrieved for download: {len(sounds)}")
        if not sounds:
            print("No sounds to download. Moving to next pages.")
        else:
            download_sounds(sounds)

        # 다음 범위로 이동
        start_page = end_page + 1
        end_page = min(start_page + 2, 3)  # 3페이지 초과하지 않도록 제한

        save_json({"start_page": start_page}, PROGRESS_FILE)



if __name__ == "__main__":
    process_pages()
