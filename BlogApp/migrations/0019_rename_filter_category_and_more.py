# Generated by Django 5.0.6 on 2024-06-04 12:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('BlogApp', '0018_alter_filter_text'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Filter',
            new_name='Category',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='filters',
            new_name='categories',
        ),
    ]
