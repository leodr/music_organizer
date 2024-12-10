def extract_spotify_track_id(url: str) -> str:
    """
    Extract the Spotify track ID from a Spotify URL.

    Args:
        url: Spotify track URL (e.g. https://open.spotify.com/track/0fch9WBS4rnE93SdSm44Zp?si=3691e7d01fee47e9)

    Returns:
        The track ID (e.g. 0fch9WBS4rnE93SdSm44Zp)
    """
    # Split on 'track/' and take the second part
    track_id = url.split("track/")[1]

    # Remove query parameters if present
    if "?" in track_id:
        track_id = track_id.split("?")[0]

    return track_id
