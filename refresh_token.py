import requests

CLIENT_ID = "4dDr1nZcw2ZUBe1eYvwE"
CLIENT_SECRET = "DYBhG9A1CTFdhTkKNidyKYkSftxLvUM1mScbmz3O"
REDIRECT_URI = "http://127.0.0.1"
AUTH_CODE = "eE5KYQomGCRLwAr1xD8hQARwJqp3tD"

token_url = "https://freesound.org/apiv2/oauth2/access_token/"
data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "authorization_code",
    "code": AUTH_CODE,
    "redirect_uri": REDIRECT_URI,
}

response = requests.post(token_url, data=data)
print(response.json())
