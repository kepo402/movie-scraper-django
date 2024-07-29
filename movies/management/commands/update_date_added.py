from django.core.management.base import BaseCommand
from movies.models import Content
from datetime import datetime

class Command(BaseCommand):
    help = 'Update the date_added field for existing Content records'

    def handle(self, *args, **kwargs):
        for content in Content.objects.all():
            if not content.date_added:
                content.date_added = datetime.now()
                content.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated date_added for all content.'))
