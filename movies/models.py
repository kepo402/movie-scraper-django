# models.py
import requests
from django.db import models

def get_new_download_link(url):
    headers = {
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

    response = requests.post(url, headers=headers, allow_redirects=False)
    
    if response.status_code == 302:
        return response.headers.get('Location')
    else:
        return None

class Content(models.Model):
    TYPE_CHOICES = [
        ('movie', 'Movie'),
        ('series', 'Series'),
        ('nollywood', 'Nollywood'),
        ('music', 'Music'),
    ]

    title = models.CharField(max_length=200)
    download_link = models.URLField(max_length=1500)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    details = models.TextField(null=True, blank=True)
    poster_url = models.URLField(max_length=300, null=True, blank=True)
    subtitle_url = models.URLField(max_length=300, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.download_link:
            new_download_link = get_new_download_link(self.download_link)
            if new_download_link:
                self.download_link = new_download_link
        super().save(*args, **kwargs)

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












