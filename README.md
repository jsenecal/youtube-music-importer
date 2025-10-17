
# YouTube Music Playlist Importer

A Python utility to automatically create and update playlists on YouTube Music using CSV files.

## Description

This tool was made for taking exported CSVs from Spotify and being able to ingest them into Youtube Music.  But, it should work for just about any CSV formatted music list.  It does depend on the [ytmusicapi](https://ytmusicapi.readthedocs.io/en/stable/) library, which is a third party library.  I have no affiliation with the author of that library.

## Prerequisites

- Docker (recommended) or Python 3.x
- YouTube Data API credentials (Client ID and Client Secret)

## Quick Start (Docker)

### Step 1: Get API Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the YouTube Data API v3
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Select "TVs and Limited Input devices" as the application type
6. Save your **Client ID** and **Client Secret**

### Step 2: Generate oauth.json

Run the OAuth setup command to create your authentication file:

```bash
docker run -it -v $(pwd):/data ghcr.io/jsenecal/youtube-music-importer:latest --setup-oauth --oauth /data/oauth.json
```

You'll be prompted to enter your Client ID and Secret, then visit a URL to authorize the application. The `oauth.json` will be saved in your current directory.

### Step 3: Prepare Your CSV Files

Prepare your CSV files with your playlists. Each CSV file will become one playlist (named after the filename).

**Default CSV columns:** The importer expects columns named `Track Name` and `Artist Name(s)` by default (matching Spotify's [Exportify](https://exportify.net/) format). If your CSV uses different column names, see the customization section below.

### Step 4: Run the Importer

```bash
docker run -v $(pwd):/data ghcr.io/jsenecal/youtube-music-importer:latest --oauth /data/oauth.json --csv-dir /data
```

Or with custom paths:
```bash
docker run \
  -v /path/to/oauth.json:/data/oauth.json \
  -v /path/to/csv-directory:/data/csvs \
  ghcr.io/jsenecal/youtube-music-importer:latest \
  --oauth /data/oauth.json \
  --csv-dir /data/csvs
```

The script will iterate over each CSV file, creating or updating the corresponding playlist on YouTube Music with the tracks specified in the CSV.

### Expected Output

If everything worked as intended, you should see something like this:

```bash
Successfully added 'Put Your Hands Up For Detroit - Radio Edit' by Fedde Le Grand to playlist 'test'.
Successfully added 'Innocence' by NERO to playlist 'test'.
Successfully added 'Pressure - Alesso Remix' by Nadia Ali,Starkillers,Alex Kenji,Alesso to playlist 'test'.
```

## Error Handling

The script implements error handling mechanisms like retrying on rate limit errors and exponential backoff; you may need to adjust if you run into issues.

---

## Advanced Usage

### Python Installation (No Docker)

If you prefer to run the script directly with Python:

1. Clone the repository:
```bash
git clone https://github.com/jsenecal/youtube-music-importer.git
cd youtube-music-importer
```

2. Install the required Python packages:
```bash
pip install ytmusicapi
```

3. Set up OAuth:
```bash
python add.py --setup-oauth
```

4. Run the importer:
```bash
python add.py
```

You can optionally specify custom paths:
```bash
python add.py --oauth /path/to/oauth.json --csv-dir /path/to/csvs
```

### Building Docker Image Locally

If you want to build the Docker image yourself instead of using the pre-built one:

1. Clone the repository:
```bash
git clone https://github.com/jsenecal/youtube-music-importer.git
cd youtube-music-importer
```

2. Build the Docker image:
```bash
docker build -t youtube-music-importer .
```

3. Use `youtube-music-importer` instead of `ghcr.io/jsenecal/youtube-music-importer:latest` in the commands above.

### Customizing CSV Column Headers

If your CSV files use different column headers than the defaults (`Track Name` and `Artist Name(s)`), you can specify custom column names using command-line arguments or environment variables.

**Using command-line arguments:**
```bash
docker run -v $(pwd):/data ghcr.io/jsenecal/youtube-music-importer:latest \
  --oauth /data/oauth.json \
  --csv-dir /data \
  --track-col "Song Title" \
  --artist-col "Artist"
```

**Using environment variables (Docker):**
```bash
docker run -v $(pwd):/data \
  -e TRACK_COL="Song Title" \
  -e ARTIST_COL="Artist" \
  ghcr.io/jsenecal/youtube-music-importer:latest \
  --oauth /data/oauth.json \
  --csv-dir /data
```

**Using environment variables (Python):**
```bash
export TRACK_COL="Song Title"
export ARTIST_COL="Artist"
python add.py
```

Or inline:
```bash
TRACK_COL="Song Title" ARTIST_COL="Artist" python add.py
```
