import sqlite3
import re
import subprocess
import os
from datetime import datetime

def generate_ytdlp_command(url, output_directory, video_quality):
    # Use regular expression to find the date and time in the URL
    pattern = re.compile(r'/(\d{4}/\d{1,2}/\d{1,2}/\d{1,2}/\d{1,2})/')
    match = pattern.search(url)

    if match:
        # Extract date and time and format it as YYYY-MM-DD-HH-MM
        date_parts = match.group(1).split('/')
        date_time_str = '-'.join([str(int(part)).zfill(2) for part in date_parts])

        # Construct the yt-dlp command
        output_path = os.path.join(output_directory, f"{date_time_str}.mp4")
        command = f'yt-dlp -f "{video_quality}" -o "{output_path}" "{url}"'
        return command, output_path
    else:
        return None, None

def download_videos_from_database(db_path, config):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the 'downloads' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            video_link TEXT PRIMARY KEY,
            m3u8_link TEXT,
            output_filename TEXT,
            timestamp TEXT
        )
    ''')

    # Fetch all downloaded m3u8 links
    cursor.execute('SELECT m3u8_link FROM downloads')
    downloaded_m3u8_links = set(row[0] for row in cursor.fetchall())

    # Fetch all streams from the 'stream_links' table
    cursor.execute('SELECT video_link, m3u8_link FROM stream_links')
    streams = cursor.fetchall()

    # Filter out streams that have already been downloaded
    streams_to_download = [stream for stream in streams if stream[1] not in downloaded_m3u8_links]

    if not streams_to_download:
        print("No new videos to download.")
        conn.close()
        return

    output_directory = config.get('output_directory', '')
    video_quality = config.get('yt_dlp_video_quality', 'bestvideo+bestaudio')

    for video_link, m3u8_link in streams_to_download:
        command, output_filename = generate_ytdlp_command(m3u8_link, output_directory, video_quality)
        if command:
            print(f"Executing command: {command}")
            try:
                # Execute the command
                subprocess.run(command, shell=True, check=True)

                # If download is successful, add to the 'downloads' table
                timestamp = datetime.now().isoformat()
                cursor.execute('''
                    INSERT INTO downloads (video_link, m3u8_link, output_filename, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (video_link, m3u8_link, output_filename, timestamp))
                conn.commit()
                print(f"Downloaded and saved: {output_filename}")
            except subprocess.CalledProcessError as e:
                print(f"An error occurred while downloading {m3u8_link}: {e}")
        else:
            print(f"URL skipped (date and time not found): {m3u8_link}")

    # Close the database connection
    conn.close()
