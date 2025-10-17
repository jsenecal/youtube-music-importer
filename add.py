from ytmusicapi import YTMusic
from ytmusicapi.setup import setup_oauth
import csv
import os
import time
import argparse

MAX_RETRIES = 4 # times
DELAY = 10  # seconds
TRACK_COL = 'Track Name'  # Modify this to the header name for tracks in your CSV
ARTIST_COL = 'Artist Name(s)'  # Modify this to the header name for artists in your CSV

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Import playlists to YouTube Music from CSV files')
parser.add_argument('--oauth', '-o', default='oauth.json', help='Path to oauth.json file (default: oauth.json)')
parser.add_argument('--csv-dir', '-d', default='.', help='Directory containing CSV files (default: current directory)')
parser.add_argument('--setup-oauth', action='store_true', help='Run OAuth setup to create oauth.json file')
parser.add_argument('--client-id', help='YouTube Data API Client ID (optional, will prompt if not provided)')
parser.add_argument('--client-secret', help='YouTube Data API Client Secret (optional, will prompt if not provided)')
args = parser.parse_args()

# If setup-oauth flag is set, run OAuth setup and exit
if args.setup_oauth:
    print("Starting OAuth setup...")
    print("")

    client_id = args.client_id
    client_secret = args.client_secret

    # Prompt for credentials if not provided
    if not client_id:
        client_id = input("Enter your Client ID: ").strip()
    if not client_secret:
        client_secret = input("Enter your Client Secret: ").strip()

    if not client_id or not client_secret:
        print("Error: Client ID and Client Secret are required")
        exit(1)

    print("\nYou will be prompted to visit a URL to authorize the application...")
    setup_oauth(filepath=args.oauth, client_id=client_id, client_secret=client_secret)
    print(f"\n✓ OAuth setup complete! {args.oauth} has been created.")
    print("You can now run the importer without the --setup-oauth flag.")
    exit(0)

# Check if oauth.json exists
if not os.path.exists(args.oauth):
    print(f"Error: {args.oauth} not found.")
    print(f"\nTo set up OAuth, run:")
    print(f"  python add.py --setup-oauth")
    print(f"\nYou'll need your Client ID and Secret from: https://console.cloud.google.com/")
    exit(1)

yt = YTMusic(args.oauth)

# Fetch existing playlists once
existing_playlists = {playlist['title']: playlist['playlistId'] for playlist in yt.get_library_playlists()}

delay = DELAY

def get_or_create_playlist(name):
    if name in existing_playlists:
        return existing_playlists[name]
    
    playlist_id = yt.create_playlist(name, name + ' description')
    existing_playlists[name] = playlist_id
    return playlist_id

csv_files = [file for file in os.listdir(args.csv_dir) if file.endswith('.csv')]

try:
    for csv_file in csv_files:
        playlist_name = os.path.splitext(csv_file)[0] 
        playlistId = get_or_create_playlist(playlist_name)
        
        with open(os.path.join(args.csv_dir, csv_file), mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                time.sleep(1)
                track = row[TRACK_COL]
                artist = row[ARTIST_COL]
                search_query = f"{track} {artist}"
                search_results = yt.search(search_query)
                

                retries = 0
                success = False

                while retries < MAX_RETRIES and not success:
                    try:
                        if search_results:
                            song_id = None
                            for result in search_results:
                                if 'videoId' in result:
                                    song_id = result['videoId']
                                    break

                            if song_id:
                                yt.add_playlist_items(playlistId, [song_id])
                                print(f"Successfully added '{track}' by {artist} to playlist '{playlist_name}'.")
                                success = True
                            else:
                                print(f"No valid videoId found for '{track}' by {artist}.")
                                success = True  # No point in retrying if song wasn't found
                        else:
                            print(f"Couldn't find '{track}' by {artist} in the search results.")
                            success = True  # No point in retrying if song wasn't found

                    except Exception as e:
                        if "HTTP 400" in str(e) or "HTTP 429" in str(e):  # 429 is typical for rate limit errors
                            print(f"Rate limit error for '{track}' by {artist}. Retrying in {delay} seconds...")
                            time.sleep(delay)
                            delay *= 2  # Double the delay for exponential backoff
                            retries += 1
                        else:
                            print(f"An error occurred while adding '{track}' by {artist} to playlist '{playlist_name}': {e}")
                            retries = MAX_RETRIES  # Don't retry for other errors

                # Reset delay for next song
                delay = DELAY

except Exception as e:
    print(f"An error occurred: {e}")

print("Finished processing all CSV files!")
