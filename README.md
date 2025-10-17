
# YouTube Music Playlist Importer

A Python utility to automatically create and update playlists on YouTube Music using CSV files.

## Description

This tool was made for taking exported CSVs from Spotify and being able to ingest them into Youtube Music.  But, it should work for just about any CSV formatted music list.  It does depend on the [ytmusicapi](https://ytmusicapi.readthedocs.io/en/stable/) library, which is a third party library.  I have no affiliation with the author of that library.

## Prerequisites

- Python 3.x
- YouTube Data API credentials (Client ID and Client Secret)
- An `oauth.json` file (generated through OAuth setup - see below)

## Setting up OAuth

Before you can use the importer, you need to set up OAuth authentication with the YouTube Music API.

### Step 1: Get API Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the YouTube Data API v3
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Select "TVs and Limited Input devices" as the application type
6. Save your **Client ID** and **Client Secret**

### Step 2: Generate oauth.json

Run the OAuth setup command:

```bash
python add.py --setup-oauth
```

You'll be prompted to:
1. Enter your Client ID
2. Enter your Client Secret
3. Visit a URL to authorize the application
4. Enter the authorization code

This will create an `oauth.json` file that the importer will use for authentication.

**Tip:** You can also provide credentials as arguments:
```bash
python add.py --setup-oauth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/bcherb2/youtube-music-importer.git yt-music-importer
```

2. Change directory into the cloned repository:
```bash
cd yt-music-importer
```

3. Install the required Python packages:
```bash
pip install ytmusicapi
```

## Docker Installation (Alternative)

If you prefer to use Docker instead of installing Python dependencies locally, you have two options:

### OAuth Setup with Docker

Before running the importer, you need to generate `oauth.json`. Run the OAuth setup interactively:

```bash
docker run -it -v $(pwd):/data ghcr.io/jsenecal/youtube-music-importer:latest --setup-oauth --oauth /data/oauth.json
```

This will prompt you for your Client ID and Secret, then guide you through the OAuth flow. The `oauth.json` will be saved in your current directory.

### Option 1: Use Pre-built Image (Recommended)

A pre-built Docker image is automatically published to GitHub Container Registry on every push to main.

Run the container with your CSV files and oauth.json mounted as volumes:
```bash
docker run \
  -v /path/to/oauth.json:/data/oauth.json \
  -v /path/to/csv-directory:/data/csvs \
  ghcr.io/jsenecal/youtube-music-importer:latest \
  --oauth /data/oauth.json \
  --csv-dir /data/csvs
```

Replace `/path/to/oauth.json` and `/path/to/csv-directory` with your actual paths.

Alternatively, if your oauth.json and CSV files are in the current directory, you can use:
```bash
docker run -v $(pwd):/data ghcr.io/jsenecal/youtube-music-importer:latest --oauth /data/oauth.json --csv-dir /data
```

### Option 2: Build Locally

1. Clone the repository and change directory:
```bash
git clone https://github.com/jsenecal/youtube-music-importer.git
cd youtube-music-importer
```

2. Build the Docker image:
```bash
docker build -t youtube-music-importer .
```

3. Run the container (use `youtube-music-importer` instead of the ghcr.io image):
```bash
docker run \
  -v /path/to/oauth.json:/data/oauth.json \
  -v /path/to/csv-directory:/data/csvs \
  youtube-music-importer \
  --oauth /data/oauth.json \
  --csv-dir /data/csvs
```

## Usage

1. Prepare your CSV files. Each CSV file should represent one playlist. The script will use the exact filename of the CSV to become (or update) the playlist.  I used [Exportify](https://exportify.net/) to export my Spotify playlists to CSV.
   
   To ensure compatibility, make sure you modify the column header variables `TRACK_COL` and `ARTIST_COL` in the script to match the column headers of your CSV files.

2. Place the CSV files in the same directory as the script.

3. Run the script:
```bash
python add.py
```

   You can optionally specify custom paths:
```bash
python add.py --oauth /path/to/oauth.json --csv-dir /path/to/csvs
```

4. The script will iterate over each CSV file, creating or updating the corresponding playlist on YouTube Music with the  tracks specified in the CSV.

If everything worked as intended, you should see something like this:

```bash
    >python .\add.py
    Successfully added 'Put Your Hands Up For Detroit - Radio Edit' by Fedde Le Grand to playlist 'test'.
    Successfully added 'Innocence' by NERO to playlist 'test'.
    Successfully added 'Pressure - Alesso Remix' by Nadia Ali,Starkillers,Alex Kenji,Alesso to playlist 'test'.
```

## Error Handling

The script implements error handling mechanisms like retrying on rate limit errors and exponential backoff; you may need to adjust if you run into issues.
