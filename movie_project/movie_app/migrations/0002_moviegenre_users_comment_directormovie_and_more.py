# Generated by Django 5.0.6 on 2024-06-21 10:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_app', '0001_initial'),
    ]

    operations = [
       migrations.CreateModel(
            name='MovieGenre',
            fields=[
                ('genre_id', models.AutoField(primary_key=True, serialize=False)),
                ('genre_name', models.CharField(max_length=10, unique=True)),
            ],
        ),
    ]
