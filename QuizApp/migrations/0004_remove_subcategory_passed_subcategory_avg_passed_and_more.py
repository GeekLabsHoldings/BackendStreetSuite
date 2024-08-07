# Generated by Django 5.0.6 on 2024-08-04 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuizApp', '0003_remove_useremail_quiz_subcategory_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subcategory',
            name='passed',
        ),
        migrations.AddField(
            model_name='subcategory',
            name='avg_passed',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='total_entries',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='total_passed',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
