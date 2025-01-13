import requests
import os

# Freesound.org API 설정
CLIENT_ID = "RITfSIf63D26oIRXUfsE"  # Freesound.org에서 발급받은 Client ID
CLIENT_SECRET = "G2uAKUnd0gZsIX5TrIFFsJcjjqmGmP8WXx3BQV2C"  # Freesound.org에서 발급받은 Client Secret
ACCESS_TOKEN = "jhbuYUt2xaZNPkxceOPiYA3y0tlkdf"  # OAuth2 Access Token
REFRESH_TOKEN = "7jrcGlqPhCgQabT9o2aA60pUgdQYiJ"  # OAuth2 Refresh Token
BASE_URL = "https://freesound.org/apiv2"

# 다운로드할 디렉토리 설정
DOWNLOAD_DIR = "freesound_effects"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def refresh_access_token():
    """
    Refresh the access token using the refresh token.
    """
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
        print("Error refreshing access token:", response.status_code, response.text)
        raise Exception("Unable to refresh access token.")

def search_effect_sounds(query=None, num_results=50):
    """
    Freesound.org에서 효과음(CC0 라이선스)을 검색합니다.
    :param query: 검색어 (효과음 전반적으로 수집하려면 None으로 설정)
    :param num_results: 검색 결과 개수
    :return: CC0 라이선스 효과음 리스트
    """
    endpoint = f"{BASE_URL}/search/text/"
    params = {
        "fields": "id,name,duration,tags,previews,license",
        "page_size": num_results,
        "filter": "license:cc0",  # CC0 필터 추가
    }
    if query:
        params["query"] = query
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    response = requests.get(endpoint, params=params, headers=headers)
    if response.status_code == 401:  # Unauthorized, refresh token
        refresh_access_token()
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.get(endpoint, params=params, headers=headers)

    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print("Error during search:", response.text)
        return []

def download_sound(sound_id, sound_name):
    """
    Freesound.org에서 음원을 다운로드합니다.
    :param sound_id: 음원의 ID
    :param sound_name: 음원의 이름
    """
    endpoint = f"{BASE_URL}/sounds/{sound_id}/download/"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    response = requests.get(endpoint, headers=headers, stream=True)
    if response.status_code == 401:  # Unauthorized, refresh token
        refresh_access_token()
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.get(endpoint, headers=headers, stream=True)

    if response.status_code == 200:
        file_path = os.path.join(DOWNLOAD_DIR, sound_name)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded: {file_path}")
    else:
        print("Error during download:", response.status_code, response.text)

if __name__ == "__main__":
    search_query = None
    number_of_results = 10

    print(f"Searching for sound effects...")
    sounds = search_effect_sounds(search_query, number_of_results)

    if sounds:
        print(f"Found {len(sounds)} sounds. Starting download...")
        for sound in sounds:
            sound_id = sound["id"]
            sound_name = sound["name"].replace(" ", "_") + ".mp3"
            download_sound(sound_id, sound_name)
    else:
        print("No sounds found.")
