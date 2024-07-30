import requests
from bs4 import BeautifulSoup
import concurrent.futures
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'custommoviesite.settings')
django.setup()

from movies.models import Content  # Adjust if your model is in a different app

def scrape_music_details(detail_url, fallback_title=None):
    response = requests.get(detail_url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code != 200:
        print(f"Failed to retrieve the music detail page. Status code: {response.status_code}")
        return None

    detail_soup = BeautifulSoup(response.text, 'html.parser')

    # Use fallback title if available, otherwise search for the title in the page
    title_tag = detail_soup.find('h1')
    title = fallback_title if fallback_title else (title_tag.get_text(strip=True) if title_tag else "Unknown Title")

    download_link_tag = detail_soup.find('a', string="DOWNLOAD MP3")
    download_link = download_link_tag['href'] if download_link_tag else None

    print(f"Scraped details for {title}:")
    print(f"  Download Link: {download_link}")

    return {
        'title': title,
        'download_link': download_link,
    }

def get_next_page_url(soup):
    next_page_link = soup.select_one('ul.pagination li a[rel="next"]')
    if next_page_link:
        next_page_url = next_page_link['href']
        if not next_page_url.startswith('http'):
            return f"https://www.val9ja.com.ng{next_page_url}"
        return next_page_url
    return None

def scrape_page(page_url, content_type):
    print(f"Fetching URL: {page_url}")
    content_items = []

    response = requests.get(page_url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return content_items

    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"Fetched URL: {page_url}")

    for article_tag in soup.select('article.nf-item'):
        link_tag = article_tag.find('a', class_='nf-image-link')
        detail_url = link_tag.get('href')
        
        img_tag = article_tag.find('img', class_='nf-image')
        img_src = img_tag['src'] if img_tag else None
        
        title_tag = article_tag.find('h3', class_='nf-title')
        title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"

        print(f"Fetching details for: {detail_url}")

        music_details = scrape_music_details(detail_url, title)
        if music_details:
            music_details['img_src'] = img_src
            music_details['type'] = content_type
            content_items.append(music_details)

    print(f"Scraped {len(content_items)} items from {page_url}")
    return content_items

def scrape_content(start_url, content_type):
    print(f"Fetching URL: {start_url}")
    all_content_items = []
    current_url = start_url

    page_urls = []
    visited_urls = set()

    while current_url and current_url not in visited_urls:
        visited_urls.add(current_url)
        page_urls.append(current_url)

        response = requests.get(current_url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Fetched URL: {current_url}")

        next_page_url = get_next_page_url(soup)
        if not next_page_url or next_page_url in visited_urls:
            break

        current_url = next_page_url
        print(f"Next page URL: {current_url}")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_page, url, content_type) for url in page_urls]
        for future in concurrent.futures.as_completed(futures):
            all_content_items.extend(future.result())

    print(f"Scraped {len(all_content_items)} items from {start_url}")
    return all_content_items

def save_content_to_db(content_items):
    saved_count = 0
    skipped_count = 0

    for item in content_items:
        if item['download_link'] is None:
            print(f"Skipping item due to missing download link: {item['title']}")
            skipped_count += 1
            continue

        # Handle cases where multiple objects might exist with the same title
        content = Content.objects.filter(title=item['title'])
        
        if content.exists():
            # If there are multiple or one, update the first found
            for obj in content:
                obj.permanent_download_link = item['download_link']
                obj.poster_url = item['img_src']
                obj.type = item['type']
                obj.details = f"Title: {item['title']}"
                obj.save()
            print(f"Updated existing content: {item['title']}")
        else:
            # Create a new entry if none exists
            Content.objects.create(
                title=item['title'],
                permanent_download_link=item['download_link'],
                poster_url=item['img_src'],
                type=item['type'],
                details=f"Title: {item['title']}",
            )
            print(f"Created new content: {item['title']}")
        
        saved_count += 1

    print(f"Saved {saved_count} items to database.")
    print(f"Skipped {skipped_count} items due to missing download links.")

if __name__ == "__main__":
    # Define URLs for scraping music
    music_urls = [
        ("https://www.val9ja.com.ng/music/page/117/", 'music'),
("https://www.val9ja.com.ng/music/page/118/", 'music'),
("https://www.val9ja.com.ng/music/page/119/", 'music'),
("https://www.val9ja.com.ng/music/page/120/", 'music'),
("https://www.val9ja.com.ng/music/page/121/", 'music'),
("https://www.val9ja.com.ng/music/page/122/", 'music'),
("https://www.val9ja.com.ng/music/page/123/", 'music'),
("https://www.val9ja.com.ng/music/page/124/", 'music'),
("https://www.val9ja.com.ng/music/page/125/", 'music'),
("https://www.val9ja.com.ng/music/page/126/", 'music'),
("https://www.val9ja.com.ng/music/page/127/", 'music'),
("https://www.val9ja.com.ng/music/page/128/", 'music'),
("https://www.val9ja.com.ng/music/page/129/", 'music'),
("https://www.val9ja.com.ng/music/page/130/", 'music'),
("https://www.val9ja.com.ng/music/page/131/", 'music'),
("https://www.val9ja.com.ng/music/page/132/", 'music'),
("https://www.val9ja.com.ng/music/page/133/", 'music'),
("https://www.val9ja.com.ng/music/page/134/", 'music'),
("https://www.val9ja.com.ng/music/page/135/", 'music'),
("https://www.val9ja.com.ng/music/page/136/", 'music'),
("https://www.val9ja.com.ng/music/page/137/", 'music'),
("https://www.val9ja.com.ng/music/page/138/", 'music'),
("https://www.val9ja.com.ng/music/page/139/", 'music'),
("https://www.val9ja.com.ng/music/page/140/", 'music'),
("https://www.val9ja.com.ng/music/page/141/", 'music'),
("https://www.val9ja.com.ng/music/page/142/", 'music'),
("https://www.val9ja.com.ng/music/page/143/", 'music'),
("https://www.val9ja.com.ng/music/page/144/", 'music'),
("https://www.val9ja.com.ng/music/page/145/", 'music'),
("https://www.val9ja.com.ng/music/page/146/", 'music'),
("https://www.val9ja.com.ng/music/page/147/", 'music'),
("https://www.val9ja.com.ng/music/page/148/", 'music'),
("https://www.val9ja.com.ng/music/page/149/", 'music'),
("https://www.val9ja.com.ng/music/page/150/", 'music'),
("https://www.val9ja.com.ng/music/page/151/", 'music'),
("https://www.val9ja.com.ng/music/page/152/", 'music'),
("https://www.val9ja.com.ng/music/page/153/", 'music'),
("https://www.val9ja.com.ng/music/page/154/", 'music'),
("https://www.val9ja.com.ng/music/page/155/", 'music'),
("https://www.val9ja.com.ng/music/page/156/", 'music'),
("https://www.val9ja.com.ng/music/page/157/", 'music'),
("https://www.val9ja.com.ng/music/page/158/", 'music'),
("https://www.val9ja.com.ng/music/page/159/", 'music'),
("https://www.val9ja.com.ng/music/page/160/", 'music'),
("https://www.val9ja.com.ng/music/page/161/", 'music'),
("https://www.val9ja.com.ng/music/page/162/", 'music'),
("https://www.val9ja.com.ng/music/page/163/", 'music'),
("https://www.val9ja.com.ng/music/page/164/", 'music'),
("https://www.val9ja.com.ng/music/page/165/", 'music'),
("https://www.val9ja.com.ng/music/page/166/", 'music'),
("https://www.val9ja.com.ng/music/page/167/", 'music'),
("https://www.val9ja.com.ng/music/page/168/", 'music'),
("https://www.val9ja.com.ng/music/page/169/", 'music'),
("https://www.val9ja.com.ng/music/page/170/", 'music'),
("https://www.val9ja.com.ng/music/page/171/", 'music'),
("https://www.val9ja.com.ng/music/page/172/", 'music'),
("https://www.val9ja.com.ng/music/page/173/", 'music'),
("https://www.val9ja.com.ng/music/page/174/", 'music'),
("https://www.val9ja.com.ng/music/page/175/", 'music'),
("https://www.val9ja.com.ng/music/page/176/", 'music'),
("https://www.val9ja.com.ng/music/page/177/", 'music'),
("https://www.val9ja.com.ng/music/page/178/", 'music'),
("https://www.val9ja.com.ng/music/page/179/", 'music'),
("https://www.val9ja.com.ng/music/page/180/", 'music'),
("https://www.val9ja.com.ng/music/page/181/", 'music'),
("https://www.val9ja.com.ng/music/page/182/", 'music'),
("https://www.val9ja.com.ng/music/page/183/", 'music'),
("https://www.val9ja.com.ng/music/page/184/", 'music'),
("https://www.val9ja.com.ng/music/page/185/", 'music'),
("https://www.val9ja.com.ng/music/page/186/", 'music'),
("https://www.val9ja.com.ng/music/page/187/", 'music'),
("https://www.val9ja.com.ng/music/page/188/", 'music'),
("https://www.val9ja.com.ng/music/page/189/", 'music'),
("https://www.val9ja.com.ng/music/page/190/", 'music'),
("https://www.val9ja.com.ng/music/page/191/", 'music'),
("https://www.val9ja.com.ng/music/page/192/", 'music'),
("https://www.val9ja.com.ng/music/page/193/", 'music'),
("https://www.val9ja.com.ng/music/page/194/", 'music'),
("https://www.val9ja.com.ng/music/page/195/", 'music'),
("https://www.val9ja.com.ng/music/page/196/", 'music'),
("https://www.val9ja.com.ng/music/page/197/", 'music'),
("https://www.val9ja.com.ng/music/page/198/", 'music'),
("https://www.val9ja.com.ng/music/page/199/", 'music'),
("https://www.val9ja.com.ng/music/page/200/", 'music'),
("https://www.val9ja.com.ng/music/page/201/", 'music'),
("https://www.val9ja.com.ng/music/page/202/", 'music'),
("https://www.val9ja.com.ng/music/page/203/", 'music'),
("https://www.val9ja.com.ng/music/page/204/", 'music'),
("https://www.val9ja.com.ng/music/page/205/", 'music'),
("https://www.val9ja.com.ng/music/page/206/", 'music'),
("https://www.val9ja.com.ng/music/page/207/", 'music'),
("https://www.val9ja.com.ng/music/page/208/", 'music'),
("https://www.val9ja.com.ng/music/page/209/", 'music'),
("https://www.val9ja.com.ng/music/page/210/", 'music'),
("https://www.val9ja.com.ng/music/page/211/", 'music'),
("https://www.val9ja.com.ng/music/page/212/", 'music'),
("https://www.val9ja.com.ng/music/page/213/", 'music'),
("https://www.val9ja.com.ng/music/page/214/", 'music'),
("https://www.val9ja.com.ng/music/page/215/", 'music'),
("https://www.val9ja.com.ng/music/page/216/", 'music'),
  ]

    all_items = []
    
    # Scrape music content
    for url, content_type in music_urls:
        items = scrape_content(url, content_type)
        all_items.extend(items)

    # Save all content items to database
    save_content_to_db(all_items)




