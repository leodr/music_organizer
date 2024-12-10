import io
import os
import random
from pathlib import Path

from mutagen import File
from PIL import Image


def get_mp3_files(music_dir):
    """Recursively find all MP3 files in the given directory."""
    mp3_files = []
    for root, _, files in os.walk(music_dir):
        for file in files:
            if file.lower().endswith(".mp3"):
                mp3_files.append(os.path.join(root, file))
    return mp3_files


def extract_cover_art(mp3_path):
    """Extract cover art from MP3 file. Returns PIL Image or None if no cover art found."""
    try:
        audio = File(mp3_path)

        # Try different tag formats
        if hasattr(audio, "tags"):
            # ID3 tags (MP3)
            if "APIC:" in audio.tags:
                artwork = audio.tags["APIC:"].data
                return Image.open(io.BytesIO(artwork))
            elif "APIC:Cover" in audio.tags:
                artwork = audio.tags["APIC:Cover"].data
                return Image.open(io.BytesIO(artwork))

        return None
    except Exception as e:
        print(f"Error extracting cover art from {mp3_path}: {e}")
        return None


def create_cover_collage(music_dir, output_path, grid_size=9):
    """Create a collage of album covers in a grid."""
    # Final image dimensions
    FINAL_SIZE = 2700
    COVER_SIZE = FINAL_SIZE // grid_size  # Size of each cover art

    # Get all MP3 files
    mp3_files = get_mp3_files(music_dir)

    if len(mp3_files) < grid_size * grid_size:
        raise ValueError(
            f"Not enough MP3 files. Found {len(mp3_files)}, need {grid_size * grid_size}"
        )

    # Create a copy of mp3_files to draw from
    available_files = mp3_files.copy()

    # Create new image with white background
    collage = Image.new("RGB", (FINAL_SIZE, FINAL_SIZE), "white")

    # Process each grid position
    for index in range(grid_size * grid_size):
        # Calculate position in grid
        row = index // grid_size
        col = index % grid_size

        cover = None
        while cover is None and available_files:
            # Get a random file
            mp3_path = random.choice(available_files)
            available_files.remove(mp3_path)  # Remove to avoid picking it again

            # Try to extract cover
            cover = extract_cover_art(mp3_path)

            if not cover:
                print(f"No cover art found for: {mp3_path}, trying another file...")

        if not cover:
            print("Warning: Ran out of files to try for this position!")
            continue

        # Resize cover art maintaining aspect ratio
        cover.thumbnail((COVER_SIZE, COVER_SIZE), Image.Resampling.LANCZOS)

        # Create white background for this cell
        cell = Image.new("RGB", (COVER_SIZE, COVER_SIZE), "white")

        # Calculate position to center cover in cell
        x = (COVER_SIZE - cover.width) // 2
        y = (COVER_SIZE - cover.height) // 2

        # Paste cover onto cell
        cell.paste(cover, (x, y))

        # Paste cell onto main image
        collage.paste(cell, (col * COVER_SIZE, row * COVER_SIZE))

    # Save the final collage
    collage.save(output_path, quality=95)
    print(f"Collage saved to: {output_path}")


if __name__ == "__main__":
    music_dir = "music/"  # Replace with your music directory path
    output_path = "cover_collage.jpg"

    try:
        create_cover_collage(music_dir, output_path)
    except Exception as e:
        print(f"Error creating collage: {e}")
