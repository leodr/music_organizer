import io
import json
import os

import requests
from dotenv import load_dotenv
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment

# Load environment variables
load_dotenv()
AUDD_API_KEY = os.getenv("AUDD_API_KEY")


def extract_audio_segment(file_path, start_sec=30, duration_sec=20):
    """Extract a segment of audio from the given file."""
    audio = AudioSegment.from_mp3(file_path)
    segment = audio[start_sec * 1000 : (start_sec + duration_sec) * 1000]

    # Export segment to bytes
    buffer = io.BytesIO()
    segment.export(buffer, format="mp3")
    return buffer.getvalue()


def recognize_song(audio_data):
    """Send audio to AudD API and get song information."""
    url = "https://api.audd.io/"

    data = {
        "api_token": AUDD_API_KEY,
        "return": "spotify",  # Request Spotify data
    }

    files = {
        "file": audio_data,
    }

    try:
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None


def update_metadata(file_path, spotify_url):
    """Update the MP3 metadata with Spotify URL."""
    try:
        audio = EasyID3(file_path)
        audio["website"] = spotify_url
        audio.save()
        return True
    except Exception as e:
        print(f"Error updating metadata for {file_path}: {e}")
        return False


def has_spotify_url(file_path):
    """Check if the file already has a Spotify URL in its metadata."""
    try:
        audio = EasyID3(file_path)
        website = audio.get("website", [None])[0]
        return website and "spotify" in website.lower()
    except Exception:
        return False


def process_file(file_path):
    """Process a single MP3 file."""
    print(f"\nProcessing: {file_path}")

    # Skip if already has Spotify URL
    if has_spotify_url(file_path):
        print("Skipping - already has Spotify URL")
        return

    # Extract audio segment
    audio_data = extract_audio_segment(file_path)

    # Recognize song
    result = recognize_song(audio_data)

    if result and result.get("status") == "success" and result.get("result"):
        song_data = result["result"]
        spotify_data = song_data.get("spotify")

        if spotify_data and spotify_data.get("external_urls"):
            spotify_url = spotify_data["external_urls"]["spotify"]
            print(f"Found match: {song_data.get('title')} by {song_data.get('artist')}")
            print(f"Spotify URL: {spotify_url}")

            # Update metadata
            if update_metadata(file_path, spotify_url):
                print("Successfully updated metadata")
            else:
                print("Failed to update metadata")
        else:
            print("No Spotify data found for this track")
    else:
        print("No match found or error in recognition")


def process_files():
    """Process all MP3 files in the unprocessed folder and its subdirectories."""
    unprocessed_dir = "music"

    # Create unprocessed directory if it doesn't exist
    if not os.path.exists(unprocessed_dir):
        print(f"Creating {unprocessed_dir} directory...")
        os.makedirs(unprocessed_dir)
        return

    # Walk through all directories and subdirectories
    for root, _, files in os.walk(unprocessed_dir):
        # Filter for MP3 files
        mp3_files = [f for f in files if f.lower().endswith(".mp3")]

        for file_name in mp3_files:
            file_path = os.path.join(root, file_name)
            process_file(file_path)

    if not any(
        f.lower().endswith(".mp3")
        for _, _, files in os.walk(unprocessed_dir)
        for f in files
    ):
        print("No MP3 files found in the unprocessed directory or its subdirectories.")


if __name__ == "__main__":
    process_files()
