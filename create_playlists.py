import os
from pathlib import Path

import spotipy
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from spotipy.oauth2 import SpotifyOAuth

from spotify_track_id import extract_spotify_track_id


def get_activity_description(bpm):
    """Return suitable activities for given BPM range."""
    if 105 <= bpm <= 115:
        return "Perfect for yoga, stretching, and light walking. Great warm-up tempo."
    elif 115 <= bpm <= 125:
        return "Ideal for power walking, light jogging, and dynamic stretching."
    elif 125 <= bpm <= 135:
        return "Great for jogging, cycling, and cardio workouts."
    elif 135 <= bpm <= 145:
        return "Perfect for running, high-intensity cardio, and dance workouts."
    elif 145 <= bpm <= 155:
        return "Ideal for sprint intervals, HIIT workouts, and intense cardio sessions."
    elif 155 <= bpm <= 165:
        return (
            "Maximum intensity! Perfect for sprint training and hardcore HIIT sessions."
        )
    return "General workout playlist"


def get_year_from_id3(audio_id3, file_path):
    """Extract year from ID3 tags, returns None if year is invalid or before 1960."""
    try:
        # Try TYER tag first
        if "TYER" in audio_id3 and audio_id3["TYER"].text[0]:
            year = int(str(audio_id3["TYER"].text[0]).strip())
        # Fall back to TDRC if TYER is not available
        elif "TDRC" in audio_id3 and audio_id3["TDRC"].text[0]:
            year = int(str(audio_id3["TDRC"].text[0]).split("-")[0])
        else:
            return None

        return year if year >= 1960 else None
    except (ValueError, TypeError, IndexError):
        print(f"Invalid year format in tags for {file_path}")
        return None


def create_m3u_playlist(name, file_paths, output_dir="playlists"):
    """Create an M3U playlist file with the given name and tracks."""
    # Create playlists directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Create m3u file
    playlist_path = output_path / f"{name}.m3u"
    with open(playlist_path, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for path in file_paths:
            # Convert to relative path from playlist location to song
            rel_path = os.path.relpath(path, start=output_path)
            f.write(f"{rel_path}\n")

    print(f"Created M3U playlist: {playlist_path}")


def create_playlists(add_to_liked_songs=True):
    """
    Create playlists and optionally add songs to liked songs or a separate playlist.

    Args:
        add_to_liked_songs (bool): If True, adds songs to liked songs. If False, creates an "All Songs" playlist.
    """
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="playlist-read-private playlist-modify-private playlist-modify-public user-library-modify",
            redirect_uri="http://127.0.0.1:9090",
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            cache_path=".new_cache",
        )
    )

    user_id = sp.current_user()["id"]
    bpm_groups = {110: [], 120: [], 130: [], 140: [], 150: [], 160: []}
    bpm_groups_files = {110: [], 120: [], 130: [], 140: [], 150: [], 160: []}
    decade_groups = {}
    decade_groups_files = {}
    folder_groups = {}
    folder_groups_files = {}
    all_track_ids = set()

    # Scan music directory
    music_dir = Path("music")
    for file_path in music_dir.rglob("*.mp3"):
        try:
            audio_easy = EasyID3(file_path)
            audio_id3 = ID3(file_path)

            # Get Spotify track ID
            spotify_url = audio_easy.get("website", [""])[0]
            track_id = extract_spotify_track_id(spotify_url)
            if not track_id:
                continue

            all_track_ids.add(track_id)

            # Group by folder name
            folder_name = file_path.parent.name
            if folder_name != "music":  # Skip the root music directory
                folder_groups.setdefault(folder_name, []).append(track_id)
                folder_groups_files.setdefault(folder_name, []).append(file_path)

            # Process BPM
            if audio_easy.get("bpm"):
                bpm = float(audio_easy["bpm"][0])
                for center_bpm in bpm_groups:
                    if center_bpm - 5 <= bpm <= center_bpm + 5:
                        bpm_groups[center_bpm].append(track_id)
                        bpm_groups_files[center_bpm].append(file_path)
                        break

            # Process year
            year = get_year_from_id3(audio_id3, file_path)
            if year:
                decade = (year // 10) * 10
                decade_groups.setdefault(decade, []).append(track_id)
                decade_groups_files.setdefault(decade, []).append(file_path)

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

    # Create BPM-based playlists
    for bpm, track_ids in bpm_groups.items():
        if not track_ids:
            continue

        playlist_name = f"Workout {bpm} BPM"

        # Create Spotify playlist
        playlist = sp.user_playlist_create(
            user_id,
            playlist_name,
            public=True,
            description=get_activity_description(bpm),
        )

        for i in range(0, len(track_ids), 100):
            sp.playlist_add_items(playlist["id"], track_ids[i : i + 100])
        print(f"Created Spotify playlist: {playlist_name} with {len(track_ids)} tracks")

        # Create M3U playlist
        create_m3u_playlist(playlist_name, bpm_groups_files[bpm])

    # Create decade-based playlists
    for decade, track_ids in sorted(decade_groups.items()):
        if not track_ids:
            continue

        playlist_name = f"Music from the {decade}s"

        # Create Spotify playlist
        playlist = sp.user_playlist_create(
            user_id,
            playlist_name,
            public=True,
            description=f"Collection of tracks from the {decade}s",
        )

        for i in range(0, len(track_ids), 100):
            sp.playlist_add_items(playlist["id"], track_ids[i : i + 100])
        print(f"Created Spotify playlist: {playlist_name} with {len(track_ids)} tracks")

        # Create M3U playlist
        create_m3u_playlist(playlist_name, decade_groups_files[decade])

    # Create folder-based playlists
    for folder_name, track_ids in sorted(folder_groups.items()):
        if not track_ids:
            continue

        # Create Spotify playlist
        playlist = sp.user_playlist_create(
            user_id,
            folder_name,
            public=True,
            description=f"Music from the {folder_name} folder",
        )

        for i in range(0, len(track_ids), 100):
            sp.playlist_add_items(playlist["id"], track_ids[i : i + 100])
        print(f"Created Spotify playlist: {folder_name} with {len(track_ids)} tracks")

        # Create M3U playlist
        create_m3u_playlist(folder_name, folder_groups_files[folder_name])

    # Handle all tracks
    track_list = list(all_track_ids)
    if add_to_liked_songs:
        # Add all tracks to user's library
        for i in range(0, len(track_list), 50):
            sp.current_user_saved_tracks_add(tracks=track_list[i : i + 50])
        print(f"Added {len(all_track_ids)} tracks to your Spotify library")
    else:
        # Create an "All Songs" playlist
        all_songs_playlist = sp.user_playlist_create(
            user_id,
            "All Songs",
            public=True,
            description="Collection of all imported tracks",
        )

        for i in range(0, len(track_list), 100):
            sp.playlist_add_items(all_songs_playlist["id"], track_list[i : i + 100])
        print(f"Created 'All Songs' playlist with {len(all_track_ids)} tracks")

        # Create M3U playlist for all songs
        create_m3u_playlist(
            "All Songs",
            [path for paths in folder_groups_files.values() for path in paths],
        )


if __name__ == "__main__":
    # You can now call create_playlists with your preferred option
    create_playlists(add_to_liked_songs=False)  # Creates "All Songs" playlist
    # or
    # create_playlists(add_to_liked_songs=True)  # Adds to liked songs (default behavior)
