# Generated by Django 5.0.6 on 2024-07-03 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CourseApp', '0013_alter_assessmentcompleted_module'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='label',
            new_name='difficulty',
        ),
        migrations.RenameField(
            model_name='course',
            old_name='subscribers',
            new_name='subscriber_number',
        ),
        migrations.RemoveField(
            model_name='course',
            name='average_completed',
        ),
        migrations.RemoveField(
            model_name='course',
            name='tag',
        ),
        migrations.AddField(
            model_name='course',
            name='time_to_complete',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='category',
            field=models.CharField(max_length=32),
        ),
    ]
