# Generated by Django 5.0.6 on 2024-06-12 09:43

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('personID', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')], default='U', max_length=1)),
                ('marital_status', models.CharField(choices=[('S', 'Single'), ('M', 'Married'), ('W', 'Widowed'), ('U', 'Unknown')], default='U', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='ProductionCompany',
            fields=[
                ('company_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('company_description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('movie_id', models.AutoField(primary_key=True, serialize=False)),
                ('moviename', models.CharField(max_length=100)),
                ('length', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(9999)])),
                ('releaseyear', models.IntegerField(blank=True, null=True)),
                ('plot_summary', models.TextField(blank=True)),
                ('resource_link', models.CharField(max_length=100, unique=True)),
                ('production_company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movie_app.productioncompany')),
            ],
        ),
    ]
