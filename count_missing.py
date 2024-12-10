import os
from collections import defaultdict
from datetime import timedelta

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from tqdm import tqdm


def format_duration(seconds):
    duration = timedelta(seconds=round(seconds))
    return str(duration)


def count_missing_website_tags(music_dir="music"):
    # Lists to store files with and without website tags
    missing_website = []
    has_website = []
    # Dictionary to store files by website value
    website_groups = defaultdict(list)

    # Get all MP3 files recursively
    mp3_files = []
    for root, dirs, files in os.walk(music_dir):
        for file in files:
            if file.lower().endswith(".mp3"):
                mp3_files.append(os.path.join(root, file))

    # Process each file with progress bar
    for mp3_path in tqdm(mp3_files, desc="Checking website tags"):
        try:
            audio = EasyID3(mp3_path)
            if "website" not in audio:
                missing_website.append(mp3_path)
            else:
                has_website.append(mp3_path)
                # Group files by website value
                website_value = audio["website"][0]
                website_groups[website_value].append(mp3_path)
        except Exception as e:
            print(f"Error processing {mp3_path}: {str(e)}")

    # Handle missing website tags
    print("\nFiles missing website tag:")
    for file in missing_website:
        try:
            mp3 = MP3(file)
            duration = format_duration(mp3.info.length)
            print(f"\n- {file} [{duration}]")
        except Exception as e:
            print(f"\n- {file} [Duration unavailable: {str(e)}]")

    # Print statistics
    total_files = len(mp3_files)
    missing_count = len(missing_website)
    has_count = len(has_website)
    unique_websites = len(website_groups)

    print("\nFinal Statistics:")
    print(f"Total MP3 files: {total_files}")
    print(f"Files with website tag: {has_count} ({(has_count/total_files)*100:.1f}%)")
    print(
        f"Files missing website tag: {missing_count} ({(missing_count/total_files)*100:.1f}%)"
    )
    print(f"Unique website values: {unique_websites}")

    # Print duplicate statistics
    print("\nDuplicate Analysis:")
    duplicates = {url: files for url, files in website_groups.items() if len(files) > 1}
    if duplicates:
        print(f"\nFound {len(duplicates)} website values with multiple files:")
        for website, files in duplicates.items():
            print(f"\nWebsite: {website}")
            print(f"Number of files: {len(files)}")
            for file in files:
                try:
                    mp3 = MP3(file)
                    duration = format_duration(mp3.info.length)
                    print(f"- {file} [{duration}]")
                except Exception as e:
                    print(f"- {file} [Duration unavailable: {str(e)}]")
    else:
        print("No duplicates found (no website values appear multiple times)")


if __name__ == "__main__":
    count_missing_website_tags()
