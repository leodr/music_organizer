def sort_tracks(tracks):
    def sort_key(track):
        album_type_priority = {"album": 1, "single": 2, "compilation": 3}
        album = track.get("album", {})
        # Determine the album type priority
        album_type = album.get(
            "album_type", "album"
        )  # Default to 'album' if not specified
        album_priority = album_type_priority.get(
            album_type, 3
        )  # Default to lowest priority

        # Parse the release date
        release_date = album.get(
            "release_date", "9999-99-99"
        )  # Fallback to a far-future date
        release_date_parts = release_date.split("-")
        release_year = (
            int(release_date_parts[0]) if release_date_parts[0].isdigit() else 9999
        )
        release_month = (
            int(release_date_parts[1])
            if len(release_date_parts) > 1 and release_date_parts[1].isdigit()
            else 99
        )
        release_day = (
            int(release_date_parts[2])
            if len(release_date_parts) > 2 and release_date_parts[2].isdigit()
            else 99
        )

        # Number of tracks
        total_tracks = album.get("total_tracks", 0)

        # Explicit content priority
        explicit = track.get("explicit", False)

        return (
            album_priority,
            release_year,
            release_month,
            release_day,
            -total_tracks,  # More tracks come first
            not explicit,  # Explicit comes first
        )

    return sorted(tracks, key=sort_key)
