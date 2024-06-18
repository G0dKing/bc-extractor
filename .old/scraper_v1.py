import requests
from bs4 import BeautifulSoup
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TARGET = os.environ.get("TARGET")

page = requests.get(
    TARGET )
soup = BeautifulSoup(page.content, 'html.parser')

song_data = []

songs = soup.select('audio')
for song in songs:
    text = song.text
    text = text.strip() if text is not None else ''
    src = song.get('src')
    alt = song.get('alt')
    href = song.get('href')
    song_data.append({"href": href, "text": text, "src": src, "alt": alt})

    print(song_data)