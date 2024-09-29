from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import time
import random
import sqlite3
import re

def find_master_m3u8_links(db_path, config):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the 'stream_links' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stream_links (
            video_link TEXT PRIMARY KEY,
            m3u8_link TEXT,
            timestamp TEXT
        )
    ''')

    # Fetch all video links from 'all_links'
    cursor.execute('SELECT video_link FROM all_links')
    all_video_links = set(row[0] for row in cursor.fetchall())

    # Fetch all processed video links from 'stream_links'
    cursor.execute('SELECT video_link FROM stream_links')
    processed_video_links = set(row[0] for row in cursor.fetchall())

    # Determine which video links need to be processed
    video_links_to_process = list(all_video_links - processed_video_links)

    if not video_links_to_process:
        print("No new video links to process for m3u8 extraction.")
        conn.close()
        return

    # Set up Chrome options
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--start-maximized")
    user_agent = config.get('user_agent', '')
    if user_agent:
        chrome_options.add_argument(f'user-agent={user_agent}')

    # Initialize the webdriver with undetected_chromedriver
    driver = uc.Chrome(options=chrome_options)

    new_streams_count = 0

    try:
        for video_link in video_links_to_process:
            print(f"Processing {video_link}...")

            # Navigate to the video page
            driver.get(video_link)

            # Wait for the page to load
            time.sleep(random.uniform(3, 5))

            # Scroll to load dynamic content if necessary
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 2))

            # Extract the page source
            page_source = driver.page_source

            # Use regex to find the 'master.m3u8' link in the page source without trailing slash
            m3u8_match = re.search(r'(https://[^\s\'"]+?/master\.m3u8)', page_source)

            if m3u8_match:
                m3u8_link = m3u8_match.group(1)
                # Insert into the 'stream_links' table
                cursor.execute('''
                    INSERT INTO stream_links (video_link, m3u8_link, timestamp)
                    VALUES (?, ?, datetime('now'))
                ''', (video_link, m3u8_link))
                conn.commit()
                new_streams_count += 1
                print(f"Found master.m3u8 link for {video_link}")
            else:
                print(f"No master.m3u8 link found for {video_link}")

            # Sleep to mimic human behavior
            time.sleep(random.uniform(1, 2))

    finally:
        # Close the browser and database connection
        driver.quit()
        conn.close()

    print(f"Inserted {new_streams_count} new stream links into 'stream_links' table.")
