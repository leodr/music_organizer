import re


def clean_string_for_filename(string: str) -> str:
    """
    Cleans a string for use as a filename by removing invalid characters.
    """
    clean = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "", string)
    return clean


def remove_song_version_info(song_title: str) -> str:
    """
    Removes remaster information from a song title.
    """
    patterns = [
        r" - Remastered \d{4}",  # Matches " - Remastered 2020"
        r" \(Remastered \d{4}\)",  # Matches " (Remastered 2020)"
        r" - \d{4} Remaster",  # Matches " - 2020 Remaster"
        r" \(.*?Remaster.*?\)",  # Matches any "(...Remaster...)" cases
        r" - Remastered$",  # Matches " - Remastered" at the end of the string
        r" - \d{4} Mix",  # Matches " - 2020 Mix"
        r" \(\d{4} Mix\)",  # Matches " (2020 Mix)"
        r" - Radio Edit$",  # Matches " - Radio Edit" at the end
        r" \(Radio Edit\)",  # Matches " (Radio Edit)"
    ]

    # Apply each pattern and remove matches
    for pattern in patterns:
        song_title = re.sub(pattern, "", song_title)

    # Remove trailing or extra spaces
    return song_title.strip()


def normalize_string(input_string: str) -> str:
    """
    Normalize a string by replacing & with "and", removing non-alphanumeric characters,
    converting to lowercase, and replacing duplicate whitespace with a single space.
    Also removes English and German articles.
    """
    # Replace & with "and"
    input_string = re.sub(r"&", "and", input_string)
    # Convert ä to ae, ö to oe, ü to ue, ß to ss
    input_string = re.sub(r"ä", "ae", input_string)
    input_string = re.sub(r"ö", "oe", input_string)
    input_string = re.sub(r"ü", "ue", input_string)
    input_string = re.sub(r"ß", "ss", input_string)

    # Remove non-alphanumeric characters, allowing spaces
    clean_string = re.sub(r"[^a-zA-Z0-9\s]", "", input_string)
    # Convert to lowercase
    clean_string = clean_string.lower()

    # Remove English and German articles
    clean_string = re.sub(r"\b(the|der|die|das)\b", "", clean_string)

    # Replace multiple spaces with a single space
    normalized_string = re.sub(r"\s+", " ", clean_string).strip()

    # Replace "yusuf cat stevens" with "cat stevens"
    normalized_string = re.sub(r"yusuf cat stevens", "cat stevens", normalized_string)

    # Replace "bob marley the wailers" with "bob marley"
    normalized_string = re.sub(
        r"bob marley and wailers", "bob marley", normalized_string
    )

    # Replace multiple spaces with a single space
    normalized_string = re.sub(r"\s+", " ", normalized_string).strip()

    return normalized_string
