# Generated by Django 5.1.7 on 2025-05-16 12:21

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mergenceApp', '0009_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='room_name',
        ),
        migrations.AlterField(
            model_name='message',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
