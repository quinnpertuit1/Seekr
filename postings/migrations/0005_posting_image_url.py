# Generated by Django 3.0.1 on 2020-01-12 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('postings', '0004_auto_20200101_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='posting',
            name='image_url',
            field=models.URLField(blank=True),
        ),
    ]