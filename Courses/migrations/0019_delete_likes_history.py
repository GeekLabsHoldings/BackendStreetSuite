# Generated by Django 5.0.6 on 2024-08-12 09:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Courses', '0018_remove_course_liked_users_course_liked_users'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Likes_history',
        ),
    ]
