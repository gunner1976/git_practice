"""One-time helper for personal-Gmail mode: prints a Drive refresh token.

    pip install google-auth-oauthlib
    python tools/get_refresh_token.py path/to/oauth-client.json

Run it on your own computer (it opens a browser to sign in).
"""
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]

if len(sys.argv) != 2:
    sys.exit(__doc__)

flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], SCOPES)
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
print("\nGOOGLE_OAUTH_CLIENT_ID     =", creds.client_id)
print("GOOGLE_OAUTH_CLIENT_SECRET =", creds.client_secret)
print("GOOGLE_OAUTH_REFRESH_TOKEN =", creds.refresh_token)
