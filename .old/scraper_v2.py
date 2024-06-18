import requests
from bs4 import BeautifulSoup
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TARGET = os.environ.get("TARGET")

response = requests.get(TARGET)
response.raise_for_status()

soup = BeautifulSoup(response.content, 'html.parser')

audio_data = []
audio_elements = soup.select('audio')

for audio in audio_elements:
    src = audio.get('src')
    alt = audio.get('alt', '')
    href = audio.get('href', '')
    text = audio.text.strip() if audio.text else ''

    audio_data.append({"href": href, "text": text, "src": src, "alt": alt})

    print({"href": href, "text": text, "src": src, "alt": alt})

for data in audio_data:
    print(data)