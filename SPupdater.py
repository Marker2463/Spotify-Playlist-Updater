import spotipy
import spotipy.util as util
import schedule
import time
import spotipy.oauth2 as oauth2


# Spotify 2 API credentials
SPOTIPY_CLIENT_ID = 'YOUR_SPOTIFY_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'YOUR_SPOTIPY_CLIENT_SECRET'
SPOTIPY_REDIRECT_URI = 'YOUR_SPOTIPY_REDIRECT_URI'
playlist_url = "your_playlist_url"
# Spotify username and scope
USERNAME = 'YOUR_USERNAME'
SCOPE = 'YOUR_SCOPE'

# Replace with your actual playlist ID
PLAYLIST_ID = 'YOUR_PLAYLIST_ID'

# Your desired new title and description
NEW_TITLE = 'YOUR_NEW_TITLE'
NEW_DESCRIPTION = 'YOUR_NEW_DESCRIPTION'

# Initialize SpotipyOAuth object
sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SCOPE, cache_path='.cache')

# Function to refresh access token
def refresh_access_token(token_info):
    refreshed_token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return refreshed_token_info['access_token']

# Authenticate and set up Spotipy object
token_info = sp_oauth.get_cached_token()
if not token_info:
    auth_url = sp_oauth.get_authorize_url()
    print("Please visit the following URL to authorize: " + auth_url)
    auth_code = input("Enter the authorization code from the URL: ")
    token_info = sp_oauth.get_access_token(auth_code)

token = token_info['access_token']
sp = spotipy.Spotify(auth=token)

# Function to update playlist details
def update_playlist_details(playlist_id, new_title, new_description):
    try:
        sp.playlist_change_details(playlist_id, name=new_title, description=new_description)
        print("Playlist details updated successfully.")
    except spotipy.SpotifyException as e:
        print("Error updating playlist details:", e)

# Check for playlist state changes and update if needed
def check_and_update_playlist(token_info):
    playlist = sp.playlist(PLAYLIST_ID)
    current_title = playlist['name']
    current_description = playlist['description']

    if current_title != NEW_TITLE or current_description != NEW_DESCRIPTION:
        update_playlist_details(PLAYLIST_ID, NEW_TITLE, NEW_DESCRIPTION)
    else:
        print("Playlist details are already up to date.")


# Schedule the check_and_update_playlist function to run every [insert time]

schedule.every(9).minutes.do(check_and_update_playlist, token_info=token_info)

#Keep the script running
while True:
    if sp_oauth.is_token_expired(token_info):
        token = refresh_access_token(token_info)
        sp = spotipy.Spotify(auth=token)
        token_info['access_token'] = token

        
    schedule.run_pending()
    time.sleep(1)
