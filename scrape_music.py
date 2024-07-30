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
        ("https://www.val9ja.com.ng/music/page/33/", 'music'),
        ("https://www.val9ja.com.ng/music/page/34/", 'music'),
        ("https://www.val9ja.com.ng/music/page/35/", 'music'),
        ("https://www.val9ja.com.ng/music/page/36/", 'music'),
        ("https://www.val9ja.com.ng/music/page/37/", 'music'),
        ("https://www.val9ja.com.ng/music/page/38/", 'music'),
        ("https://www.val9ja.com.ng/music/page/39/", 'music'),
        ("https://www.val9ja.com.ng/music/page/40/", 'music'),
        ("https://www.val9ja.com.ng/music/page/41/", 'music'),
        ("https://www.val9ja.com.ng/music/page/42/", 'music'),
        ("https://www.val9ja.com.ng/music/page/43/", 'music'),
        ("https://www.val9ja.com.ng/music/page/44/", 'music'),
        ("https://www.val9ja.com.ng/music/page/45/", 'music'),
        ("https://www.val9ja.com.ng/music/page/46/", 'music'),
        ("https://www.val9ja.com.ng/music/page/47/", 'music'),
        ("https://www.val9ja.com.ng/music/page/48/", 'music'),
        ("https://www.val9ja.com.ng/music/page/49/", 'music'),
        ("https://www.val9ja.com.ng/music/page/50/", 'music'),
        ("https://www.val9ja.com.ng/music/page/51/", 'music'),
        ("https://www.val9ja.com.ng/music/page/52/", 'music'),
        ("https://www.val9ja.com.ng/music/page/53/", 'music'),
        ("https://www.val9ja.com.ng/music/page/54/", 'music'),
        ("https://www.val9ja.com.ng/music/page/55/", 'music'),
        ("https://www.val9ja.com.ng/music/page/56/", 'music'),
        ("https://www.val9ja.com.ng/music/page/57/", 'music'),
        ("https://www.val9ja.com.ng/music/page/58/", 'music'),
        ("https://www.val9ja.com.ng/music/page/59/", 'music'),
        ("https://www.val9ja.com.ng/music/page/60/", 'music'),
        ("https://www.val9ja.com.ng/music/page/61/", 'music'),
        ("https://www.val9ja.com.ng/music/page/62/", 'music'),
        ("https://www.val9ja.com.ng/music/page/63/", 'music'),
        ("https://www.val9ja.com.ng/music/page/64/", 'music'),
        ("https://www.val9ja.com.ng/music/page/65/", 'music'),
        ("https://www.val9ja.com.ng/music/page/66/", 'music'),
        ("https://www.val9ja.com.ng/music/page/67/", 'music'),
        ("https://www.val9ja.com.ng/music/page/68/", 'music'),
        ("https://www.val9ja.com.ng/music/page/69/", 'music'),
        ("https://www.val9ja.com.ng/music/page/70/", 'music'),
        ("https://www.val9ja.com.ng/music/page/71/", 'music'),
        ("https://www.val9ja.com.ng/music/page/72/", 'music'),
        ("https://www.val9ja.com.ng/music/page/73/", 'music'),
        ("https://www.val9ja.com.ng/music/page/74/", 'music'),
        ("https://www.val9ja.com.ng/music/page/75/", 'music'),
        ("https://www.val9ja.com.ng/music/page/76/", 'music'),
        ("https://www.val9ja.com.ng/music/page/77/", 'music'),
        ("https://www.val9ja.com.ng/music/page/78/", 'music'),
        ("https://www.val9ja.com.ng/music/page/79/", 'music'),
        ("https://www.val9ja.com.ng/music/page/80/", 'music'),
        ("https://www.val9ja.com.ng/music/page/81/", 'music'),
        ("https://www.val9ja.com.ng/music/page/82/", 'music'),
        ("https://www.val9ja.com.ng/music/page/83/", 'music'),
        ("https://www.val9ja.com.ng/music/page/84/", 'music'),
        ("https://www.val9ja.com.ng/music/page/85/", 'music'),
        ("https://www.val9ja.com.ng/music/page/86/", 'music'),
        ("https://www.val9ja.com.ng/music/page/87/", 'music'),
        ("https://www.val9ja.com.ng/music/page/88/", 'music'),
        ("https://www.val9ja.com.ng/music/page/89/", 'music'),
        ("https://www.val9ja.com.ng/music/page/90/", 'music'),
        ("https://www.val9ja.com.ng/music/page/91/", 'music'),
        ("https://www.val9ja.com.ng/music/page/92/", 'music'),
        ("https://www.val9ja.com.ng/music/page/93/", 'music'),
        ("https://www.val9ja.com.ng/music/page/94/", 'music'),
        ("https://www.val9ja.com.ng/music/page/95/", 'music'),
        ("https://www.val9ja.com.ng/music/page/96/", 'music'),
        ("https://www.val9ja.com.ng/music/page/97/", 'music'),
        ("https://www.val9ja.com.ng/music/page/98/", 'music'),
        ("https://www.val9ja.com.ng/music/page/99/", 'music'),
        ("https://www.val9ja.com.ng/music/page/100/", 'music'),
        ("https://www.val9ja.com.ng/music/page/101/", 'music'),
        ("https://www.val9ja.com.ng/music/page/102/", 'music'),
        ("https://www.val9ja.com.ng/music/page/103/", 'music'),
        ("https://www.val9ja.com.ng/music/page/104/", 'music'),
        ("https://www.val9ja.com.ng/music/page/105/", 'music'),
        ("https://www.val9ja.com.ng/music/page/106/", 'music'),
        ("https://www.val9ja.com.ng/music/page/107/", 'music'),
        ("https://www.val9ja.com.ng/music/page/108/", 'music'),
        ("https://www.val9ja.com.ng/music/page/109/", 'music'),
        ("https://www.val9ja.com.ng/music/page/110/", 'music'),
        ("https://www.val9ja.com.ng/music/page/111/", 'music'),
        ("https://www.val9ja.com.ng/music/page/112/", 'music'),
        ("https://www.val9ja.com.ng/music/page/113/", 'music'),
        ("https://www.val9ja.com.ng/music/page/114/", 'music'),
        ("https://www.val9ja.com.ng/music/page/115/", 'music'),
        ("https://www.val9ja.com.ng/music/page/116/", 'music'),

    ]

    all_items = []
    
    # Scrape music content
    for url, content_type in music_urls:
        items = scrape_content(url, content_type)
        all_items.extend(items)

    # Save all content items to database
    save_content_to_db(all_items)




