"""
This module extracts and downloads audio links from specified web pages,
including individual tracks, albums, and playlists listed in an external file.
"""

import os
import time
from os.path import join, dirname
import re

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException
)

# Load environment variables from .env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TARGETS_FILE = os.environ.get("TARGETS_FILE", "targets.txt")

def setup_driver():
    """Set up and return a configured Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.binary_location = "/usr/bin/google-chrome"
    service = Service('/root/chromedriver')
    return webdriver.Chrome(service=service, options=chrome_options)

def get_page_content(url):
    """Fetch and return the page content for a given URL."""
    driver = setup_driver()
    driver.get(url)

    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    # Click the Play button if it exists
    try:
        play_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@class="playbutton"]'))
        )
        play_button.click()
        time.sleep(5)
    except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
        print(f"No play button found or error clicking it: {e}")

    # Parse the page content with BeautifulSoup
    content = driver.page_source
    driver.quit()
    return content

def extract_audio_links(content):
    """Extract audio links from the given page content."""
    soup = BeautifulSoup(content, 'html.parser')
    audio_data = []

    # Extract audio elements from the main page
    audio_elements = soup.select('audio')
    for audio in audio_elements:
        src = audio.get('src')
        if src:
            audio_data.append(src)

    # Extract audio elements from iframes
    iframe_elements = soup.select('iframe')
    for iframe in iframe_elements:
        iframe_src = iframe.get('src')
        if iframe_src:
            try:
                iframe_response = requests.get(iframe_src, timeout=10)
                iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')
                iframe_audio_elements = iframe_soup.select('audio')
                for audio in iframe_audio_elements:
                    src = audio.get('src')
                    if src:
                        audio_data.append(src)
            except requests.RequestException:
                print(f"Error fetching iframe content: {iframe_src}")

    return audio_data

def download_audio(url, filename):
    """Download audio from the given URL and save it with the given filename."""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded: {filename}")
    except requests.RequestException as e:
        print(f"Error downloading {filename}: {e}")

def process_url(url):
    """Process a given URL, extracting and downloading audio content."""
    print(f"Processing URL: {url}")
    content = get_page_content(url)
    soup = BeautifulSoup(content, 'html.parser')
    # Check if it's an album or playlist
    track_list = soup.select('.track-list .track-title a')
    if track_list:
        print("Album or playlist detected. Processing all tracks...")
        for track in track_list:
            track_url = track['href']
            if not track_url.startswith('http'):
                track_url = f"https://bandcamp.com{track_url}"
            process_url(track_url)
    else:
        # Single track
        audio_links = extract_audio_links(content)
        if audio_links:
            track_title = soup.select_one('.trackTitle')
            if track_title:
                filename = f"{track_title.text.strip()}.mp3"
            else:
                filename = f"track_{int(time.time())}.mp3"
            filename = re.sub(r'[^\w\-_\. ]', '_', filename)
            download_audio(audio_links[0], filename)
        else:
            print("No audio links found on this page.")

def main():
    """Main function to process all target URLs from the external file."""
    if not os.path.exists(TARGETS_FILE):
        print(f"Targets file '{TARGETS_FILE}' not found. "
              "Please create it and add your target URLs.")
        return

    with open(TARGETS_FILE, 'r', encoding='utf-8') as file:
        for line in file:
            url = line.strip()
            if url:
                process_url(url)
            else:
                print("Skipping empty line in targets file.")

if __name__ == "__main__":
    main()
