import requests

CLIENT_ID = "RITfSIf63D26oIRXUfsE"
CLIENT_SECRET = "G2uAKUnd0gZsIX5TrIFFsJcjjqmGmP8WXx3BQV2C"
REDIRECT_URI = "http://127.0.0.1"
AUTH_CODE = "gn8tvzq2BuT607dNLyVlBsBiftrkOf"

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
