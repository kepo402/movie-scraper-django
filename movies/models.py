from django.db import models

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












