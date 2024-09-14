import os
import django
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'custommoviesite.settings')
django.setup()

from movies.models import Content

def get_lulacloud_download_link(awafim_url):
    options = Options()
    options.headless = True
    service = Service(r"C:\chromedriver-win32\chromedriver-win32\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(awafim_url)
    wait = WebDriverWait(driver, 10)

    try:
        download_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.download-btn')))
        driver.execute_script("arguments[0].scrollIntoView(true);", download_button)
        driver.implicitly_wait(2)
        driver.execute_script("arguments[0].click();", download_button)
        wait.until(EC.url_changes(awafim_url))
        redirected_url = driver.current_url
        driver.quit()
        return redirected_url

    except Exception as e:
        driver.quit()
        print(f"Error occurred while getting LulaCloud link: {e}")
        return None

def scrape_movie_details(detail_url, content_type, fallback_title=None):
    try:
        response = requests.get(detail_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve the movie detail page. Error: {e}")
        return None

    detail_soup = BeautifulSoup(response.text, 'html.parser')

    try:
        if content_type == 'series':
            title_tag = detail_soup.find('h1', id='page-h1')
            title = fallback_title if fallback_title else (title_tag.get_text(strip=True) if title_tag else "Unknown Title")
        else:
            title_tag = detail_soup.find('div', id='page-h1-con').find('h1', id='page-h1')
            title = title_tag.get_text(strip=True) if title_tag else fallback_title if fallback_title else "Unknown Title"

        img_tag = detail_soup.find('img', class_='poster') or detail_soup.find('div', class_='te-thumb').find('img')
        plot_tag = detail_soup.find('p', class_='tei-plot')

        release_date = "Release date not available"
        country = "Country not available"
        language = "Language not available"
        genre = "Genre not available"

        for li in detail_soup.select('.tei-list > li'):
            name_tag = li.find('div', class_='tei-name')
            value_tag = li.find('div', class_='tei-value')
            if not name_tag or not value_tag:
                continue

            name = name_tag.get_text(strip=True)
            value = value_tag.get_text(strip=True)

            if name == 'Release Date':
                release_date = value
            elif name == 'Country':
                country = value
            elif name == 'Language':
                language = value
            elif name == 'Genre':
                genre = value

        img_src = img_tag['src'] if img_tag else None
        plot = plot_tag.get_text(strip=True) if plot_tag else "Plot not available"

        print(f"Scraped details for {title}:")
        print(f"  Image Source: {img_src}")
        print(f"  Plot: {plot}")
        print(f"  Release Date: {release_date}")
        print(f"  Country: {country}")
        print(f"  Language: {language}")
        print(f"  Genre: {genre}")

        return {
            'title': title,
            'img_src': img_src,
            'plot': plot,
            'release_date': release_date,
            'country': country,
            'language': language,
            'genre': genre
        }
    except Exception as e:
        print(f"Error occurred while scraping movie details: {e}")
        return None

def get_next_page_url(soup):
    next_page_link = soup.select_one('ul.pagination li a[rel="next"]')
    if next_page_link:
        next_page_url = next_page_link['href']
        if not next_page_url.startswith('http'):
            return f"https://www.awafim.tv{next_page_url}"
        return next_page_url
    return None

def scrape_page(page_url, content_type):
    print(f"Fetching URL: {page_url}")
    content_items = []

    try:
        response = requests.get(page_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve the page. Error: {e}")
        return content_items

    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"Fetched URL: {page_url}")

    for article_tag in soup.select('article.titles-one'):
        try:
            link_tag = article_tag.find('a')
            link = link_tag.get('href')
            if not link.startswith('http'):
                detail_url = f"https://www.awafim.tv{link}"
            else:
                detail_url = link

            img_tag = article_tag.find('img', class_='to-thumb')
            img_src = img_tag['src'] if img_tag else None

            title_tag = article_tag.find('h3', class_='to-h3')
            title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"

            if content_type == 'series':
                run_info_tag = article_tag.find('div', class_='toi-run')
                run_info = run_info_tag.get_text(strip=True) if run_info_tag else ""
                full_title = f"{title} {run_info}".strip()
            else:
                full_title = title

            print(f"Fetching details for: {detail_url}")

            movie_details = scrape_movie_details(detail_url, content_type, full_title)
            if movie_details:
                movie_details['img_src'] = img_src  # Update image source if needed
                lulacloud_link = get_lulacloud_download_link(detail_url)
                movie_details['link'] = lulacloud_link
                movie_details['type'] = content_type
                content_items.append(movie_details)
        except Exception as e:
            print(f"Error occurred while processing article: {e}")

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

        try:
            response = requests.get(current_url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to retrieve the page. Error: {e}")
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
            try:
                all_content_items.extend(future.result())
            except Exception as e:
                print(f"Error occurred while scraping page: {e}")

    print(f"Scraped {len(all_content_items)} items from {start_url}")
    return all_content_items

def save_content_to_db(content_items):
    for item in content_items:
        try:
            is_nollywood = 'NGA' in item['country']
            movie_types = set([item['type']])
            
            if item['type'] == 'movie' and is_nollywood:
                movie_types.add('nollywood')

            for movie_type in movie_types:
                Content.objects.update_or_create(
                    title=item['title'],
                    type=movie_type,
                    defaults={
                        'permanent_download_link': item['link'],
                        'poster_url': item['img_src'],
                        'details': f"Plot: {item['plot']}\nRelease Date: {item['release_date']}\nCountry: {item['country']}",
                    }
                )
        except Exception as e:
            print(f"Error occurred while saving to database: {e}")
    print(f"Saved {len(content_items)} items to database.")

if __name__ == "__main__":
    urls = [
# ("https://www.awafim.tv/browse/page/57?type=series", 'series'),
# ("https://www.awafim.tv/browse/page/247?type=movie", 'movie'),
("https://www.awafim.tv/browse/page/1?type=series", 'series'),



    ]
    

    all_items = []
    for url, content_type in urls:
        items = scrape_content(url, content_type)
        all_items.extend(items)

    save_content_to_db(all_items)


