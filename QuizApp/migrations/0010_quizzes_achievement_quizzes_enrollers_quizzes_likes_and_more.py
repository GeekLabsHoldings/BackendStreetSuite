# Generated by Django 5.0.6 on 2024-06-10 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuizApp', '0009_quizzes_description_quizzes_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizzes',
            name='achievement',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='quizzes',
            name='enrollers',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='quizzes',
            name='likes',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='quizzes',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]
