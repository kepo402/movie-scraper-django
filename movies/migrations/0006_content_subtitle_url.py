# Generated by Django 5.0.7 on 2024-07-20 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0005_alter_content_download_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='subtitle_url',
            field=models.URLField(blank=True, max_length=300, null=True),
        ),
    ]