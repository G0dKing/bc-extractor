"""
This module extracts audio links from a specified web page using Selenium and BeautifulSoup.
"""

import os
import time
from os.path import join, dirname

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
TARGET = os.environ.get("TARGET")

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.binary_location = "/usr/bin/google-chrome"
service = Service('/root/chromedriver')

driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get(TARGET)

# Wait for the page to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

# Click the Play button
try:
    play_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@class="playbutton"]'))
    )
    play_button.click()
    time.sleep(5)
except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
    print(f"Error clicking play button: {e}")
    driver.quit()
    exit()

# Parse the page content with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

# Extract audio information
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

# Save extracted audio links to a .txt file or print a message if no data found
if audio_data:
    with open('audio_links.txt', 'w', encoding='utf-8') as file:
        for link in audio_data:
            file.write(f"{link}\n")
    print(f"Extracted {len(audio_data)} audio links saved to 'audio_links.txt'.")
else:
    print("No audio links found.")
