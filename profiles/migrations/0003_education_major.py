# Generated by Django 3.0.1 on 2020-01-03 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_auto_20191229_1834'),
    ]

    operations = [
        migrations.AddField(
            model_name='education',
            name='major',
            field=models.CharField(default='', max_length=64),
        ),
    ]
