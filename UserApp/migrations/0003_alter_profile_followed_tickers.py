# Generated by Django 5.0.6 on 2024-10-01 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserApp', '0002_profile_followed_tickers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='followed_tickers',
            field=models.JSONField(default=list),
        ),
    ]
