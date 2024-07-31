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
         ("https://www.val9ja.com.ng/music/page/317/", 'music'),
("https://www.val9ja.com.ng/music/page/318/", 'music'),
("https://www.val9ja.com.ng/music/page/319/", 'music'),
("https://www.val9ja.com.ng/music/page/320/", 'music'),
("https://www.val9ja.com.ng/music/page/321/", 'music'),
("https://www.val9ja.com.ng/music/page/322/", 'music'),
("https://www.val9ja.com.ng/music/page/323/", 'music'),
("https://www.val9ja.com.ng/music/page/324/", 'music'),
("https://www.val9ja.com.ng/music/page/325/", 'music'),
("https://www.val9ja.com.ng/music/page/326/", 'music'),
("https://www.val9ja.com.ng/music/page/327/", 'music'),
("https://www.val9ja.com.ng/music/page/328/", 'music'),
("https://www.val9ja.com.ng/music/page/329/", 'music'),
("https://www.val9ja.com.ng/music/page/330/", 'music'),
("https://www.val9ja.com.ng/music/page/331/", 'music'),
("https://www.val9ja.com.ng/music/page/332/", 'music'),
("https://www.val9ja.com.ng/music/page/333/", 'music'),
("https://www.val9ja.com.ng/music/page/334/", 'music'),
("https://www.val9ja.com.ng/music/page/335/", 'music'),
("https://www.val9ja.com.ng/music/page/336/", 'music'),
("https://www.val9ja.com.ng/music/page/337/", 'music'),
("https://www.val9ja.com.ng/music/page/338/", 'music'),
("https://www.val9ja.com.ng/music/page/339/", 'music'),
("https://www.val9ja.com.ng/music/page/340/", 'music'),
("https://www.val9ja.com.ng/music/page/341/", 'music'),
("https://www.val9ja.com.ng/music/page/342/", 'music'),
("https://www.val9ja.com.ng/music/page/343/", 'music'),
("https://www.val9ja.com.ng/music/page/344/", 'music'),
("https://www.val9ja.com.ng/music/page/345/", 'music'),
("https://www.val9ja.com.ng/music/page/346/", 'music'),
("https://www.val9ja.com.ng/music/page/347/", 'music'),
("https://www.val9ja.com.ng/music/page/348/", 'music'),
("https://www.val9ja.com.ng/music/page/349/", 'music'),
("https://www.val9ja.com.ng/music/page/350/", 'music'),
("https://www.val9ja.com.ng/music/page/351/", 'music'),
("https://www.val9ja.com.ng/music/page/352/", 'music'),
("https://www.val9ja.com.ng/music/page/353/", 'music'),
("https://www.val9ja.com.ng/music/page/354/", 'music'),
("https://www.val9ja.com.ng/music/page/355/", 'music'),
("https://www.val9ja.com.ng/music/page/356/", 'music'),
("https://www.val9ja.com.ng/music/page/357/", 'music'),
("https://www.val9ja.com.ng/music/page/358/", 'music'),
("https://www.val9ja.com.ng/music/page/359/", 'music'),
("https://www.val9ja.com.ng/music/page/360/", 'music'),
("https://www.val9ja.com.ng/music/page/361/", 'music'),
("https://www.val9ja.com.ng/music/page/362/", 'music'),
("https://www.val9ja.com.ng/music/page/363/", 'music'),
("https://www.val9ja.com.ng/music/page/364/", 'music'),
("https://www.val9ja.com.ng/music/page/365/", 'music'),
("https://www.val9ja.com.ng/music/page/366/", 'music'),
("https://www.val9ja.com.ng/music/page/367/", 'music'),
("https://www.val9ja.com.ng/music/page/368/", 'music'),
("https://www.val9ja.com.ng/music/page/369/", 'music'),
("https://www.val9ja.com.ng/music/page/370/", 'music'),
("https://www.val9ja.com.ng/music/page/371/", 'music'),
("https://www.val9ja.com.ng/music/page/372/", 'music'),
("https://www.val9ja.com.ng/music/page/373/", 'music'),
("https://www.val9ja.com.ng/music/page/374/", 'music'),
("https://www.val9ja.com.ng/music/page/375/", 'music'),
("https://www.val9ja.com.ng/music/page/376/", 'music'),
("https://www.val9ja.com.ng/music/page/377/", 'music'),
("https://www.val9ja.com.ng/music/page/378/", 'music'),
("https://www.val9ja.com.ng/music/page/379/", 'music'),
("https://www.val9ja.com.ng/music/page/380/", 'music'),
("https://www.val9ja.com.ng/music/page/381/", 'music'),
("https://www.val9ja.com.ng/music/page/382/", 'music'),
("https://www.val9ja.com.ng/music/page/383/", 'music'),
("https://www.val9ja.com.ng/music/page/384/", 'music'),
("https://www.val9ja.com.ng/music/page/385/", 'music'),
("https://www.val9ja.com.ng/music/page/386/", 'music'),
("https://www.val9ja.com.ng/music/page/387/", 'music'),
("https://www.val9ja.com.ng/music/page/388/", 'music'),
("https://www.val9ja.com.ng/music/page/389/", 'music'),
("https://www.val9ja.com.ng/music/page/390/", 'music'),
("https://www.val9ja.com.ng/music/page/391/", 'music'),
("https://www.val9ja.com.ng/music/page/392/", 'music'),
("https://www.val9ja.com.ng/music/page/393/", 'music'),
("https://www.val9ja.com.ng/music/page/394/", 'music'),
("https://www.val9ja.com.ng/music/page/395/", 'music'),
("https://www.val9ja.com.ng/music/page/396/", 'music'),
("https://www.val9ja.com.ng/music/page/397/", 'music'),
("https://www.val9ja.com.ng/music/page/398/", 'music'),
("https://www.val9ja.com.ng/music/page/399/", 'music'),
("https://www.val9ja.com.ng/music/page/400/", 'music'),
("https://www.val9ja.com.ng/music/page/401/", 'music'),
("https://www.val9ja.com.ng/music/page/402/", 'music'),
("https://www.val9ja.com.ng/music/page/403/", 'music'),
("https://www.val9ja.com.ng/music/page/404/", 'music'),
("https://www.val9ja.com.ng/music/page/405/", 'music'),
("https://www.val9ja.com.ng/music/page/406/", 'music'),
("https://www.val9ja.com.ng/music/page/407/", 'music'),
("https://www.val9ja.com.ng/music/page/408/", 'music'),
("https://www.val9ja.com.ng/music/page/409/", 'music'),
("https://www.val9ja.com.ng/music/page/410/", 'music'),
("https://www.val9ja.com.ng/music/page/411/", 'music'),
("https://www.val9ja.com.ng/music/page/412/", 'music'),
("https://www.val9ja.com.ng/music/page/413/", 'music'),
("https://www.val9ja.com.ng/music/page/414/", 'music'),
("https://www.val9ja.com.ng/music/page/415/", 'music'),
("https://www.val9ja.com.ng/music/page/416/", 'music'),

    ]

    all_items = []
    
    # Scrape music content
    for url, content_type in music_urls:
        items = scrape_content(url, content_type)
        all_items.extend(items)

    # Save content to database
    save_content_to_db(all_items)





