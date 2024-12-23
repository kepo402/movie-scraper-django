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
    try:
        response = requests.get(detail_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve the music detail page. Error: {e}")
        return None

    try:
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
    except Exception as e:
        print(f"Error occurred while scraping music details: {e}")
        return None

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

    try:
        response = requests.get(page_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve the page. Error: {e}")
        return content_items

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Fetched URL: {page_url}")

        for article_tag in soup.select('article.nf-item'):
            try:
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
            except Exception as e:
                print(f"Error occurred while processing article: {e}")

        print(f"Scraped {len(content_items)} items from {page_url}")
    except Exception as e:
        print(f"Error occurred while parsing page: {e}")

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

        try:
            response = requests.get(current_url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to retrieve the page. Error: {e}")
            break

        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"Fetched URL: {current_url}")

            next_page_url = get_next_page_url(soup)
            if not next_page_url or next_page_url in visited_urls:
                break

            current_url = next_page_url
            print(f"Next page URL: {current_url}")
        except Exception as e:
            print(f"Error occurred while parsing page: {e}")
            break

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_page, url, content_type) for url in page_urls]
        for future in concurrent.futures.as_completed(futures):
            try:
                all_content_items.extend(future.result())
            except Exception as e:
                print(f"Error occurred while scraping page: {e}")

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

        try:
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
        except Exception as e:
            print(f"Error occurred while saving to database: {e}")

    print(f"Saved {saved_count} items to database.")
    print(f"Skipped {skipped_count} items due to missing download links.")

if __name__ == "__main__":
    # Define URLs for scraping music
    music_urls = [
         ("https://www.val9ja.com.ng/music/page/1/", 'music'),


    ]

    all_items = []
    
    # Scrape music content
    for url, content_type in music_urls:
        items = scrape_content(url, content_type)
        all_items.extend(items)

    # Save content to database
    save_content_to_db(all_items)





