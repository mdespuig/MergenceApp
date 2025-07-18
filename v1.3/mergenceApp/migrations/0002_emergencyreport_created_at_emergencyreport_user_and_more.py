# Generated by Django 5.1.7 on 2025-05-14 10:52

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mergenceApp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='emergencyreport',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='emergencyreport',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='emergencyreport',
            name='hotline_category',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='emergencyreport',
            name='hotline_detail',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='emergencyreport',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='emergencyreport',
            name='surname',
            field=models.CharField(max_length=255),
        ),
    ]
