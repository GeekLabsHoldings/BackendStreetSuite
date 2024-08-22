# Generated by Django 5.0.6 on 2024-08-07 08:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Courses', '0010_module_slug'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CompletedModules',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='module_complete', to='Courses.module')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_complete', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]