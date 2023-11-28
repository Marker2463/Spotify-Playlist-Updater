import spotipy
import spotipy.util as util
import schedule
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import subprocess  # Added subprocess module for Termux URL opening


# Spotify 2 API credentials
SPOTIPY_CLIENT_ID = 'YOUR_SPOTIFY_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'YOUR_SPOTIPY_CLIENT_SECRET'
SPOTIPY_REDIRECT_URI = 'YOUR_SPOTIPY_REDIRECT_URI'
# Replace with your actual playlist ID
PLAYLIST_ID = 'YOUR_PLAYLIST_ID'
# Your desired new title and description
NEW_TITLE = 'YOUR_NEW_TITLE'
NEW_DESCRIPTION = 'YOUR_NEW_DESCRIPTION'

# Configure retry strategy for requests
retry_strategy = Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

print ("Program Started ")
# Set up the web server to handle the callback
class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        query_params = self.path.split('?')[1]
        auth_code = None
        for param in query_params.split('&'):
            key, value = param.split('=')
            if key == 'code':
                auth_code = value
                break
        if auth_code:
            self.wfile.write(b'Authorization code obtained. You can close this window now.')
            global received_auth_code
            received_auth_code = auth_code
        else:
            self.wfile.write(b'Failed to obtain authorization code. Please try again.')

server = HTTPServer(('localhost', 8200), CallbackHandler)

# Replace 'your_cache_directory' with the actual path to your Termux internal storage's cache directory
cache_path = "/storage/emulated/0/spotify_cache"

# Authenticate and set up Spotipy object
sp_oauth = spotipy.oauth2.SpotifyOAuth(
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope='playlist-modify-public',
    cache_path=os.path.join(cache_path, '.cache')
)

received_auth_code = None

def open_authorization_url():
    auth_url = sp_oauth.get_authorize_url()
    print("Please visit the following URL to authorize:")
    print(auth_url)
    # Use subprocess to open the URL in Termux's default browser
    subprocess.run(["termux-open-url", auth_url])

def get_authorization_code():
    open_authorization_url()
#    auth_code = input("Enter the authorization code from the URL: ")
 #   return auth_code

token_info = sp_oauth.get_cached_token()
if not token_info:
    auth_code = get_authorization_code()
    token_info = sp_oauth.get_access_token(auth_code)

token = token_info['access_token']
sp = spotipy.Spotify(auth=token)

def update_playlist_details(playlist_id, new_title, new_description):
    try:
        sp.playlist_change_details(playlist_id, name=new_title, description=new_description)
        print("Playlist details updated successfully.")
    except spotipy.SpotifyException as e:
        print("Error updating playlist details:", e)

def check_and_update_playlist(token_info):
    playlist = sp.playlist(PLAYLIST_ID)
    current_title = playlist['name']
    current_description = playlist['description']
    if current_title != NEW_TITLE or current_description != NEW_DESCRIPTION:
        update_playlist_details(PLAYLIST_ID, NEW_TITLE, NEW_DESCRIPTION)
    else:
        print("Playlist details are already up to date.")

# Schedule to open the authorization URL and check/update the playlist every 32 minutes
schedule.every(32).minutes.do(open_authorization_url)
schedule.every(32).minutes.do(check_and_update_playlist, token_info=token_info)

# Keep the script running
while True:
    if sp_oauth.is_token_expired(token_info):
        auth_code = get_authorization_code()
        token_info = sp_oauth.get_access_token(auth_code)
        token = token_info['access_token']
        sp = spotipy.Spotify(auth=token)
    schedule.run_pending()
    time.sleep(1)