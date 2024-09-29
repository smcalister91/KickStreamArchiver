# Kick Stream Video Archiver

This project is designed to automate the process of archiving a Kick streamer's videos by scraping their video page, extracting `.m3u8` links, and downloading the streams for offline storage. The program uses Selenium with `undetected-chromedriver`, `yt-dlp` for video downloading, and stores data in an SQLite database to track which videos have already been downloaded. This program is intended to be ran every 24 hours or whatever interval you choose, which you can schedule for instance with Task Scheduler on Windows.

Streams will be named with their time and date stamp, for instance "2023-09-30-20-58.mp4"

## Setup and Usage

### Prerequisites

- Python 3.6+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (Make sure it's installed and available in your system's PATH)
- Chrome browser

### Required Python Packages

Install the required packages using `pip`:

```bash
pip install selenium undetected-chromedriver blinker==1.7.0
```

> **Note:** The program requires **Blinker version 1.7.0** specifically.

### Configuration

Before running the program, you need to configure the `config.json` file. Below is a description of each configuration option:

```json
{
    "streamer_video_page": "https://kick.com/XQC/videos",
    "yt_dlp_video_quality": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "output_directory": "Z:\\Path\\To\\Videos\\",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "database_file": "video_data.db"
}
```

- **`streamer_video_page`**: The URL of the streamer's page containing videos to scrape.
- **`yt_dlp_video_quality`**: Quality of the video to download (default set to 720p).
- **`output_directory`**: Directory to save downloaded videos.
- **`user_agent`**: The user agent string to use for web scraping.
- **`database_file`**: SQLite database file used to store video, stream, and download information.

### How to Run

1. **Clone the Repository**

   Clone this repository to your local machine.

2. **Configure the Program**

   Edit the `config.json` file with the appropriate settings.

3. **Run the Main Script**

   To start scraping and downloading videos, run:

   ```bash
   python main.py
   ```

The program will:

- Scrape the streamer's video page for new video links.
- Extract `.m3u8` links from the scraped video pages.
- Download videos that have not yet been archived.

## How It Works

1. **Scraping Video Links**

   The program uses Selenium with `undetected-chromedriver` to scrape all video links from the streamer's video page. These links are stored in the `all_links` table in the SQLite database.

2. **Extracting `.m3u8` Links**

   Each video link is visited, and its `.m3u8` stream link is extracted. This is stored in the `stream_links` table in the database.

3. **Downloading Videos**

   Using `yt-dlp`, the program downloads videos that have not yet been archived. Each successfully downloaded video is recorded in the `downloads` table, ensuring it will not be re-downloaded.

## File Structure

- **`main.py`**: The main orchestrator script that runs all the steps.
- **`config.json`**: Configuration file for customizable settings.
- **`linkFinder.py`**: Scrapes the streamer's video page to find all video links.
- **`streamLinkFinder.py`**: Extracts `.m3u8` stream links for videos.
- **`downloadStreams.py`**: Downloads videos from extracted `.m3u8` links.
- **`video_data.db`**: SQLite database used to store video links, stream links, and download records.

## Additional Information

- **Database Structure**: The database contains three main tables:
  - **`all_links`**: Stores scraped video links and their timestamps.
  - **`stream_links`**: Stores the `.m3u8` links for each video and their timestamps.
  - **`downloads`**: Stores downloaded video information, including the output filename and timestamp.

- **Error Handling**: If a video fails to download, the program will print an error message and continue processing the next video.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to modify the configurations and customize the program as needed. If you encounter any issues or have suggestions, please open an issue or submit a pull request on GitHub. Happy archiving! 🚀
