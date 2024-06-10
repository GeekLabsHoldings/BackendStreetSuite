# Generated by Django 5.0.6 on 2024-06-10 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuizApp', '0014_rename_name_category_text'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='quizzes',
        ),
        migrations.AddField(
            model_name='quizzes',
            name='categories',
            field=models.ManyToManyField(to='QuizApp.category'),
        ),
    ]
