# Generated by Django 5.1.7 on 2025-05-14 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmergencyReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('surname', models.CharField(max_length=100)),
                ('contact_number', models.CharField(max_length=15)),
                ('hotline_category', models.CharField(max_length=50)),
                ('hotline_detail', models.CharField(max_length=100)),
            ],
        ),
    ]
