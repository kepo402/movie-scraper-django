from django.db import models

class Content(models.Model):
    TYPE_CHOICES = [
        ('movie', 'Movie'),
        ('series', 'Series'),
        ('nollywood', 'Nollywood'),
        ('music', 'Music'),
    ]

    title = models.CharField(max_length=200)
    download_link = models.URLField(max_length=300)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    details = models.TextField(null=True, blank=True)
    poster_url = models.URLField(max_length=300, null=True, blank=True)
    subtitle_url = models.URLField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.title











