# Generated by Django 5.0.6 on 2024-11-11 15:15

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Courses', '0043_rename_answers_answer_rename_articles_article_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Subscribed_courses',
            new_name='Subscribed_course',
        ),
    ]
