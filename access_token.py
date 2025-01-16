import webbrowser

CLIENT_ID = "4dDr1nZcw2ZUBe1eYvwE"
REDIRECT_URI = "http://127.0.0.1"
AUTHORIZE_URL = f"https://freesound.org/apiv2/oauth2/authorize/?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"

webbrowser.open(AUTHORIZE_URL)