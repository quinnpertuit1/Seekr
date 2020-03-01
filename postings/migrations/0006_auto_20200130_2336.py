# Generated by Django 3.0.1 on 2020-01-30 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('postings', '0005_posting_image_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='posting',
            name='location',
        ),
        migrations.AddField(
            model_name='posting',
            name='city',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='posting',
            name='country',
            field=models.CharField(default='', max_length=16),
        ),
        migrations.AddField(
            model_name='posting',
            name='state',
            field=models.CharField(default='', max_length=8),
        ),
    ]