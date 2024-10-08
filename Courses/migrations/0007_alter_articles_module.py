# Generated by Django 5.0.6 on 2024-08-06 11:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Courses', '0006_subscribed_courses'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articles',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_modules', to='Courses.module'),
        ),
    ]
