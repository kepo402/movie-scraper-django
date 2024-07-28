# myapp/management/commands/update_requires_special_headers.py

from django.core.management.base import BaseCommand
from movies.models import Content

class Command(BaseCommand):
    help = 'Update requires_special_headers_1 field for existing Content objects'

    def handle(self, *args, **kwargs):
        contents = Content.objects.all()
        for content in contents:
            if content.type in ['movie', 'series', 'nollywood']:
                content.requires_special_headers_1 = True
            else:
                content.requires_special_headers_1 = False
            content.save(update_fields=['requires_special_headers_1'])
        self.stdout.write(self.style.SUCCESS('Successfully updated requires_special_headers_1 for all contents'))
