# Generated by Django 5.0.6 on 2024-09-12 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Courses', '0025_remove_question_assessment_delete_answer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='published_date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
