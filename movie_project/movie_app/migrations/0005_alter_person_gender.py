# Generated by Django 5.0.6 on 2024-06-04 02:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_app', '0004_alter_person_birth_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')], default='U', max_length=1, null=True),
        ),
    ]
