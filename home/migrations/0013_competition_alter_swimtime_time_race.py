# Generated by Django 4.1.2 on 2022-12-14 13:06

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_rename_swimtime_personalbest_swim_time_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comp_name', models.CharField(max_length=50, verbose_name='Competition Name')),
                ('location', models.CharField(max_length=150, verbose_name='Competition Location')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
        ),
        migrations.AlterField(
            model_name='swimtime',
            name='time',
            field=models.DurationField(default=datetime.timedelta(seconds=61, microseconds=10000), verbose_name='Time'),
        ),
        migrations.CreateModel(
            name='Race',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.PositiveIntegerField(default=50, verbose_name='Distance')),
                ('strokeType', models.CharField(choices=[('FC', 'Front Crawl'), ('BC', 'Back Crawl'), ('BF', 'Butterfly'), ('BS', 'Breaststroke')], default='FC', max_length=20, verbose_name='Stroke Type')),
                ('age_range', models.PositiveIntegerField()),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.competition')),
                ('swimmers', models.ManyToManyField(to='home.swimmer')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
