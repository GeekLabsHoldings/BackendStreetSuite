# Generated by Django 5.0.6 on 2024-06-09 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuizApp', '0002_alter_quizzes_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizzes',
            name='duration',
            field=models.PositiveSmallIntegerField(blank=True, default=0, null=True),
        ),
    ]
