import json
import os
from pathlib import Path


def load_dict_from_json(file_path: Path) -> dict:
    """
    Load a dictionary from a JSON file, with a fallback to an empty dictionary if the file is missing or corrupted.
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}. Returning an empty dictionary.")
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error loading JSON file: {e}. Returning an empty dictionary.")
        return {}


def save_dict_to_json(data: dict, file_path: Path):
    """Save a dictionary to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
