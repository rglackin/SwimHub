# Generated by Django 4.1.2 on 2022-11-14 14:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_alter_swimmer_dob'),
    ]

    operations = [
        migrations.AlterField(
            model_name='swimmer',
            name='dob',
            field=models.DateField(default=datetime.date(2010, 1, 1), verbose_name='Date Of Birth'),
        ),
        migrations.AlterField(
            model_name='swimmer',
            name='first_name',
            field=models.CharField(max_length=50, verbose_name='First Name'),
        ),
        migrations.AlterField(
            model_name='swimmer',
            name='last_name',
            field=models.CharField(max_length=50, verbose_name='Last Name'),
        ),
        migrations.AlterField(
            model_name='swimtime',
            name='strokeType',
            field=models.CharField(choices=[('FC', 'Front Crawl'), ('BC', 'Back Crawl'), ('BF', 'Butterfly'), ('BS', 'Breaststroke')], default='FC', max_length=20, verbose_name='Stroke Type'),
        ),
        migrations.AlterField(
            model_name='swimtime',
            name='time',
            field=models.TimeField(default=50),
        ),
    ]