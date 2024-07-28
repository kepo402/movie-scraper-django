from django.db import models
import requests
from bs4 import BeautifulSoup

def get_new_download_link(url, requires_special_headers_1=False, requires_special_headers_2=False):
    # Define headers for special cases
    headers_special_1 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.lulacloud.com',
        'Referer': url,
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Upgrade-Insecure-Requests': '1',
    }

    headers_special_2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 OPR/112.0.0.0',
        'Accept': '*/*',
        'Accept-Encoding': 'identity;q=1, *;q=0',
        'Accept-Language': 'en-US,en;q=0.9',
        'Priority': 'i',
        'Range': 'bytes=0-',
        'Referer': 'https://en4.onlinevideoconverter.pro/',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Opera";v="112"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'video',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'cross-site',
        'X-Client-Data': 'CLzqygE=',
    }

    if requires_special_headers_1:
        response = requests.post(url, headers=headers_special_1, allow_redirects=False)
        if response.status_code == 302:
            return response.headers.get('Location')
    elif requires_special_headers_2:
        response = requests.get(url, headers=headers_special_2, allow_redirects=False)
        if response.status_code == 302:
            return response.headers.get('Location')
    else:
        response = requests.get(url, allow_redirects=True)
        if response.status_code == 200:
            return response.url
    return None

def scrape_content(url, content_type, requires_special_headers_1=False):
    headers_special_1 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.lulacloud.com',
        'Referer': url,
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Upgrade-Insecure-Requests': '1',
    }

    if requires_special_headers_1:
        response = requests.get(url, headers=headers_special_1)
    else:
        response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Adjust selectors based on content type
    content_selectors = {
        'movie': 'div.movie-reel a',        # Example selector for movies
        'series': 'div.series-reel a',      # Example selector for series
    }

    selector = content_selectors.get(content_type, 'div.movie-reel a')

    content_items = []
    for item in soup.select(selector):
        link = item.get('href')
        img_tag = item.find('img')
        img_src = img_tag['src'] if img_tag else None
        img_alt = img_tag['alt'] if img_tag else None
        title = img_alt if img_alt else "Unknown Title"

        content_items.append({
            'title': title,
            'link': link,
            'img_src': img_src
        })
    
    return content_items

class Content(models.Model):
    TYPE_CHOICES = [
        ('movie', 'Movie'),
        ('series', 'Series'),
        ('nollywood', 'Nollywood'),
        ('music', 'Music'),
    ]

    title = models.CharField(max_length=200)
    permanent_download_link = models.URLField(max_length=1500)  # Original, unchanging URL
    current_download_link = models.URLField(max_length=1500, blank=True, null=True)  # Temporary URL
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    details = models.TextField(null=True, blank=True)
    poster_url = models.URLField(max_length=300, null=True, blank=True)
    subtitle_url = models.URLField(max_length=300, null=True, blank=True)

    requires_special_headers_1 = models.BooleanField(default=False)  # Header set 1
    requires_special_headers_2 = models.BooleanField(default=False)  # Header set 2

    def save(self, *args, **kwargs):
        if self.type in ['movie', 'series', 'nollywood']:
            self.requires_special_headers_1 = True
        else:
            self.requires_special_headers_1 = False
        super().save(*args, **kwargs)

    def update_download_link(self):
        if self.permanent_download_link:
            new_download_link = get_new_download_link(
                self.permanent_download_link,
                requires_special_headers_1=self.requires_special_headers_1,
                requires_special_headers_2=self.requires_special_headers_2
            )
            if new_download_link:
                self.current_download_link = new_download_link
                self.save(update_fields=['current_download_link'])
                # Move current download link to permanent download link only for header set 2
                if self.requires_special_headers_2:
                    self.permanent_download_link = new_download_link
                    self.save(update_fields=['permanent_download_link'])
                return self.current_download_link
        return None

    def revert_to_permanent_link(self):
        if self.permanent_download_link:
            self.current_download_link = self.permanent_download_link
            self.save(update_fields=['current_download_link'])

    def __str__(self):
        return self.title

class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # Choices for star ratings (1-5)

    content = models.ForeignKey(Content, related_name='reviews', on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user_name} on {self.content.title}'

