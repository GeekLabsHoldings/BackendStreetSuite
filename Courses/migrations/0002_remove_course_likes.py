# Generated by Django 5.0.6 on 2024-08-06 07:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Courses', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='likes',
        ),
    ]
