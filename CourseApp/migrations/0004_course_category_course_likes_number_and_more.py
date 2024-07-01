# Generated by Django 5.0.6 on 2024-06-26 14:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CourseApp', '0003_remove_assessment_course_assessment_module'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='category',
            field=models.CharField(choices=[('options', 'Options'), ('stock', 'Stock'), ('day_trading', 'Day Trading')], default='options', max_length=20),
        ),
        migrations.AddField(
            model_name='course',
            name='likes_number',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='module',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='assessments', to='CourseApp.module'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='course',
            name='user',
        ),
        migrations.CreateModel(
            name='Likes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CourseApp.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='courses_author', to=settings.AUTH_USER_MODEL),
        ),
    ]