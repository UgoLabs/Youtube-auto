from google_auth_oauthlib.flow import InstalledAppFlow
from config import GOOGLE_REDIRECT_URI  # import your redirect URI from config

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRETS_FILE = 'client_secret.json'

flow = InstalledAppFlow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES
)

# Set the redirect URI directly (instead of reading from flow.client_config)
flow.redirect_uri = GOOGLE_REDIRECT_URI

auth_url, _ = flow.authorization_url(prompt='consent')
print("Please visit this URL to authenticate:")
print(auth_url)

