# Generated by Django 3.0.3 on 2020-02-24 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('postings', '0001_initial'),
        ('messenger_users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='messengeruser',
            name='clicked_postings',
            field=models.ManyToManyField(related_name='clicks', to='postings.Posting'),
        ),
    ]
