import requests
from bs4 import BeautifulSoup
import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'custommoviesite.settings')
django.setup()

from movies.models import Content

BASE_URL = 'https://netnaija.xyz'
MOVIES_URL = f'{BASE_URL}'
SERIES_URL = 'https://series.netnaija.xyz'

def scrape_content(content_type, page_url):
    response = requests.get(page_url)
    if response.status_code != 200:
        print(f"Failed to fetch {page_url}. Status code: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    items = soup.select('div.movie-item')
    if content_type == 'series':
        items = soup.select('div.series-item')
    
    contents = []
    for item in items:
        title = item.select_one('h2.title').text.strip()
        download_link = item.select_one('a.download')['href']
        details = item.select_one('div.description').text.strip() if item.select_one('div.description') else None
        poster_url = item.select_one('img')['src'] if item.select_one('img') else None

        content = Content(
            title=title,
            download_link=download_link,
            type=content_type,
            details=details,
            poster_url=poster_url
        )
        contents.append(content)
    
    return contents

def scrape_movies():
    page_number = 1
    while True:
        movie_page_url = f'{MOVIES_URL}/page/{page_number}/'
        movies = scrape_content('movie', movie_page_url)
        
        if not movies:
            break
        
        Content.objects.bulk_create(movies)
        
        page_number += 1
        time.sleep(0.5)  # Reduced delay to half a second for faster processing

def scrape_series():
    page_number = 1
    while True:
        series_page_url = f'{SERIES_URL}/page/{page_number}/'
        series = scrape_content('series', series_page_url)
        
        if not series:
            break
        
        Content.objects.bulk_create(series)
        
        page_number += 1
        time.sleep(0.5)  # Reduced delay to half a second for faster processing

if __name__ == '__main__':
    scrape_movies()
    scrape_series()



