# Generated by Django 5.0.6 on 2024-11-12 10:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Courses', '0045_course_completed_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='likes_number',
        ),
    ]
