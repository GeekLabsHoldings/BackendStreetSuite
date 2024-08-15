# Generated by Django 5.0.6 on 2024-08-12 08:21

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Courses', '0017_alter_course_liked_users'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='liked_users',
        ),
        migrations.AddField(
            model_name='course',
            name='liked_users',
            field=models.ManyToManyField(blank=True, null=True, related_name='liked_users', to=settings.AUTH_USER_MODEL),
        ),
    ]
