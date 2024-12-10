import re


def parse_year(date_string):
    """
    Extracts the year from a date string.

    Args:
        date_string (str): The date string in formats like "YYYY-MM-DD", "YYYY-MM", or "YYYY".

    Returns:
        int: The year as an integer.

    Raises:
        ValueError: If no valid year is found in the string.
    """
    match = re.match(r"^\d{4}", date_string)
    if match:
        return int(match.group(0))
    raise ValueError("Invalid date string format: Year not found")
