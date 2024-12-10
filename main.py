import os
from pathlib import Path

import mutagen
import requests
import spotipy
from dotenv import load_dotenv
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3, TORY, TYER
from pydub import AudioSegment
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm

from bpm import get_bpm
from levenshtein import levenshtein_distance_ignore_word_order
from parse_year import parse_year
from safe_json import load_dict_from_json, save_dict_to_json
from sort_tracks import sort_tracks
from spotify_track_id import extract_spotify_track_id
from string_cleaning import (
    clean_string_for_filename,
    normalize_string,
    remove_song_version_info,
)

load_dotenv()

LEVENSHTEIN_DISTANCE_THRESHOLD = 2


def update_metadata(file: Path, track: dict):
    cover_image_url = track["album"]["images"][0]["url"]

    # Download the cover art if it doesn't exist
    cover_image_path = Path(f"cover_art/{track['album']['id']}.jpg")
    if not cover_image_path.exists():
        with open(cover_image_path, "wb") as f:
            f.write(requests.get(cover_image_url).content)

    # Load the file and check if it has a header
    try:
        audio = EasyID3(file)
    except mutagen.id3.ID3NoHeaderError:
        audio = mutagen.File(file, easy=True)
        audio.add_tags()

    title = track["name"]
    artist = track["artists"][0]["name"]

    audio = EasyID3(file)
    audio["title"] = title
    audio["artist"] = artist
    audio["album"] = track["album"]["name"]
    audio["website"] = track["external_urls"]["spotify"]

    if "isrc" in track["external_ids"] and track["external_ids"]["isrc"]:
        audio["isrc"] = track["external_ids"]["isrc"]

    audio["tracknumber"] = str(track["track_number"])
    audio["discnumber"] = str(track["disc_number"])

    if "bpm" not in audio:
        try:
            audio["bpm"] = get_bpm(file)
        except:
            print(f"Failed to get BPM for {file.name}")
            pass

    audio.save(v2_version=3)

    audio = ID3(file)
    year = parse_year(track["album"]["release_date"])

    audio["TORY"] = TORY(encoding=3, text=[year])
    audio["TYER"] = TYER(encoding=3, text=[year])

    with open(cover_image_path, "rb") as albumart:
        audio["APIC"] = APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=albumart.read(),
        )
    audio.save(v2_version=3)

    # New filename
    new_filename = f"{artist} - {title}"

    clean_name = clean_string_for_filename(remove_song_version_info(new_filename))

    if file.stem == clean_name:
        return

    new_file = file.with_stem(clean_name).with_suffix(file.suffix.lower())

    return file.rename(new_file)


distances_savefile_path = Path("distances.json")
distance_dict = load_dict_from_json(distances_savefile_path)


def convert_to_mp3(file: Path) -> Path:
    """
    Converts a file to mp3 and deletes the original file.
    """
    mp3_file = file.with_suffix(".mp3")

    audio = AudioSegment.from_file(file, format=file.suffix[1:])
    audio.export(mp3_file, format="mp3")
    print(f"Converted: {file.name} -> {mp3_file.name}")

    file.unlink()
    print(f"Deleted: {file}")

    return mp3_file


def update_metadata_batch(files_and_tracks: list[tuple[Path, dict]]):
    """
    Update metadata for multiple files in batch
    """
    for file, track in tqdm(
        files_and_tracks, desc="Processing files", unit="file", leave=False
    ):
        try:
            update_metadata(file, track)
        except Exception as e:
            print(f"Failed to update metadata for {file.name}: {e}")


if __name__ == "__main__":
    spotify = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        ),
    )

    all_files = list(Path("music").glob("**/*.*"))
    loaded_files = 0
    processed_files = 0

    # Store files that need track info fetching
    pending_tracks = []  # List of (file, track_id) tuples

    # First pass - identify files that need processing
    for file in tqdm(all_files, desc="Identifying files", unit="file"):
        loaded_files += 1

        # Skip unsupported extensions
        if file.suffix.lower() not in [".mp3", ".flac", ".m4a"]:
            continue

        # Convert to mp3 if necessary
        if file.suffix.lower() in [".m4a", ".flac"]:
            try:
                file = convert_to_mp3(file)
            except Exception as e:
                print(f"Failed to convert {file.name}: {e}")
                continue

        # Check if file already has Spotify metadata
        try:
            audio = EasyID3(file)
            if "website" in audio and "spotify" in audio["website"][0]:
                spotify_id = extract_spotify_track_id(audio["website"][0])
                pending_tracks.append((file, spotify_id))
                continue
        except:
            pass

        # Search for track if no Spotify metadata exists
        normalized_name = normalize_string(file.stem)

        if normalized_name in distance_dict:
            distance = distance_dict[normalized_name]
            if distance > LEVENSHTEIN_DISTANCE_THRESHOLD:
                print(f"Skipping {file.name} because it has a distance of {distance}")
                continue

        results = spotify.search(q=normalized_name, type="track", market="DE")

        if not results["tracks"]["items"]:
            print(f"Skipping {file.name} because no results were found")
            continue

        results = sort_tracks(results["tracks"]["items"])
        matched_tracks = []

        for track in results:
            correct_name = normalize_string(
                track["artists"][0]["name"]
                + " - "
                + remove_song_version_info(track["name"])
            )

            distance = levenshtein_distance_ignore_word_order(
                correct_name, normalized_name
            )

            if (
                normalized_name not in distance_dict
                or distance < distance_dict[normalized_name]
            ):
                distance_dict[normalized_name] = distance
                print(f"Correct name:    {correct_name}")
                print(f"Normalized name: {normalized_name}")
                print(f"Distance:        {distance}\n")

            if distance <= LEVENSHTEIN_DISTANCE_THRESHOLD:
                matched_tracks.append(track)

        save_dict_to_json(distance_dict, distances_savefile_path)

        if matched_tracks:
            pending_tracks.append((file, matched_tracks[0]["id"]))
        else:
            print(f"Skipping {file.name} because no matches were found")

    # Process pending tracks in batches of 50
    for i in tqdm(
        range(0, len(pending_tracks), 50), desc="Processing batches", unit="batch"
    ):
        batch = pending_tracks[i : i + 50]
        track_ids = [track_id for _, track_id in batch]

        try:
            print(f"Fetching {len(track_ids)} tracks")
            print(track_ids)
            tracks_info = spotify.tracks(track_ids, market="DE")["tracks"]
            print(f"Fetched {len(tracks_info)} tracks")
            files_and_tracks = [
                (file, track_info) for (file, _), track_info in zip(batch, tracks_info)
            ]
            update_metadata_batch(files_and_tracks)
            processed_files += len(files_and_tracks)
        except Exception as e:
            print(f"Failed to process batch: {e}")

    print(f"Processed {processed_files} out of {loaded_files} files")
