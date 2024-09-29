from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import time
import random

def find_video_links(page_url, config):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--start-maximized")
    user_agent = config.get('user_agent', '')
    if user_agent:
        chrome_options.add_argument(f'user-agent={user_agent}')

    # Set up the webdriver with undetected_chromedriver
    driver = uc.Chrome(options=chrome_options)

    try:
        # Navigate to the webpage
        driver.get(page_url)

        # Wait for the page to load
        time.sleep(random.uniform(2, 4))

        # Find all the video links on the page
        video_links = driver.find_elements(By.XPATH, "//a[@href and contains(@href, '/videos/')]")

        # Extract the URLs from the video links
        urls = list(set(link.get_attribute("href") for link in video_links))

        # Print the number of extracted URLs
        print(f"Found {len(urls)} unique video links.")

        return urls

    finally:
        # Close the browser
        driver.quit()
