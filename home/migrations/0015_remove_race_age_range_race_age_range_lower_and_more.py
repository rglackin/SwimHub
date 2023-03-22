# Generated by Django 4.1.2 on 2022-12-14 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_alter_race_age_range'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='race',
            name='age_range',
        ),
        migrations.AddField(
            model_name='race',
            name='age_range_lower',
            field=models.PositiveSmallIntegerField(default=12),
        ),
        migrations.AddField(
            model_name='race',
            name='age_range_upper',
            field=models.PositiveSmallIntegerField(default=15),
        ),
    ]
