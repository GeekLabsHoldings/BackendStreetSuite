# Generated by Django 5.0.6 on 2024-06-11 08:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('QuizApp', '0021_useremail_alter_answer_question_alter_question_quiz'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='difficulty',
        ),
        migrations.RemoveField(
            model_name='question',
            name='technique',
        ),
    ]
