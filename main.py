import json
from linkFinder import find_video_links
from streamLinkFinder import find_master_m3u8_links
from downloadStreams import download_videos_from_database
import sqlite3

def main():
    # Load configuration
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    # Step 1: Scrape Video Links
    page_url = config['streamer_video_page']
    print("Scraping video links...")
    video_urls = find_video_links(page_url, config)

    # Connect to the database
    db_path = config['database_file']
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the 'all_links' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS all_links (
            video_link TEXT PRIMARY KEY,
            timestamp TEXT
        )
    ''')

    # Insert new video links into the database
    new_links_count = 0
    for link in video_urls:
        try:
            cursor.execute('''
                INSERT INTO all_links (video_link, timestamp)
                VALUES (?, datetime('now'))
            ''', (link,))
            new_links_count += 1
        except sqlite3.IntegrityError:
            # Link already exists
            pass

    conn.commit()
    conn.close()
    print(f"Inserted {new_links_count} new video links into 'all_links' table.")

    # Step 2: Extract m3u8 Links
    print("Extracting m3u8 links...")
    find_master_m3u8_links(db_path, config)

    # Step 3: Download Videos
    print("Downloading videos...")
    download_videos_from_database(db_path, config)

if __name__ == "__main__":
    main()
