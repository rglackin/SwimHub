# Generated by Django 4.1.2 on 2022-12-08 20:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_alter_swimtime_time_personalbest'),
    ]

    operations = [
        migrations.RenameField(
            model_name='personalbest',
            old_name='swimTime',
            new_name='swim_time',
        ),
        migrations.AlterUniqueTogether(
            name='personalbest',
            unique_together={('swimmer', 'swim_time')},
        ),
    ]
