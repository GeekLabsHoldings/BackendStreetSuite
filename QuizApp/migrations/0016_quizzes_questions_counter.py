# Generated by Django 5.0.6 on 2024-06-10 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuizApp', '0015_remove_category_quizzes_quizzes_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizzes',
            name='questions_counter',
            field=models.SmallIntegerField(default=0),
        ),
    ]
