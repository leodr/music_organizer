# Music Organizer

A comprehensive Python-based music library organizer that integrates with
Spotify to manage, organize, and create playlists from your local music
collection. This tool helps you maintain a well-organized music library with
proper metadata, cover art, and synchronized Spotify playlists.

## Features

- Automatic metadata updating from Spotify
- Cover art downloading and embedding
- BPM (tempo) detection
- Smart track matching using Levenshtein distance
- Playlist generation (both M3U and Spotify):
  - BPM-based workout playlists
  - Decade-based playlists
  - Folder-based playlists
- File format conversion (FLAC/M4A to MP3)
- Automatic file renaming based on metadata
- Cover art collage generation

## Prerequisites

- Python 3.8 or higher
- Spotify Developer Account (for API access)
- AudD API key (for music recognition)

## Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd music_organizer
```

2. Install required Python packages:

```bash
pip install mutagen requests spotipy python-dotenv pydub tqdm
```

3. Create a `.env` file in the project root with your API credentials:

```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
AUDD_API_KEY=your_audd_api_key
```

4. Create the following directory structure:

```
music_organizer/
├── music/         # Place your music files here
├── cover_art/     # Auto-generated folder for album artwork
└── playlists/     # Auto-generated folder for M3U playlists
```

## Usage

### Main Music Organization Script

The main script processes your music files, updates metadata, and organizes your
library:

```bash
python main.py
```

This will:

- Convert FLAC/M4A files to MP3
- Match songs with Spotify tracks
- Update metadata (title, artist, album, year, etc.)
- Download and embed cover art
- Rename files based on metadata

### Create Playlists

Generate both M3U and Spotify playlists based on your library:

```bash
python create_playlists.py
```

This creates:

- BPM-based workout playlists (110-160 BPM ranges)
- Decade-based playlists
- Folder-based playlists
- All Songs playlist or adds songs to Spotify Liked Songs

### Additional Tools

1. Create Cover Art Collage:

```bash
python create_cover_collage.py
```

2. Count Missing Metadata:

```bash
python count_missing.py
```

## File Structure

- `main.py`: Core functionality for organizing music files
- `create_playlists.py`: Playlist generation script
- `create_cover_collage.py`: Creates album art collages
- `count_missing.py`: Reports on missing metadata
- `recognize.py`: Music recognition functionality
- Utility modules:
  - `bpm.py`: BPM detection
  - `string_cleaning.py`: String normalization and cleaning
  - `levenshtein.py`: String similarity matching
  - `parse_year.py`: Release date parsing
  - `safe_json.py`: JSON handling utilities
  - `sort_tracks.py`: Track sorting logic
  - `spotify_track_id.py`: Spotify ID extraction

## Notes

- The tool uses Levenshtein distance for fuzzy matching of track names
- Files are automatically renamed based on the pattern: "Artist - Title"
- Special characters are handled and cleaned in filenames
- Cover art is stored locally to avoid repeated downloads
- BPM detection is performed only if not already present in metadata

## Contributing

Feel free to submit issues and enhancement requests!
