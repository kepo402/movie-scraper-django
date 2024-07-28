# myapp/management/commands/scrape_content.py

from django.core.management.base import BaseCommand
from movies.models import Content
from movies.scraper import scrape_content  # Import the scraping function

class Command(BaseCommand):
    help = 'Scrape movies and series from the specified URL and update Content model'

    def add_arguments(self, parser):
        parser.add_argument('content_type', type=str, choices=['movie', 'series'], help='Type of content to scrape')
        parser.add_argument('url', type=str, help='URL to scrape')

    def handle(self, *args, **options):
        url = options['url']
        content_type = options['content_type']
        requires_special_headers_1 = True  # Set this to True or False based on your need

        # Call the scraping function
        content_items = scrape_content(url, content_type, requires_special_headers_1)

        for item in content_items:
            # Check if the content already exists
            content, created = Content.objects.get_or_create(
                title=item['title'],
                defaults={
                    'permanent_download_link': item['link'],
                    'poster_url': item['img_src'],
                    'type': content_type,
                    'details': 'Scraped content'
                }
            )
            
            if not created:
                # Update existing content if needed
                content.permanent_download_link = item['link']
                content.poster_url = item['img_src']
                content.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully scraped and updated {content_type}.'))

