# Generated by Django 5.0.6 on 2024-05-27 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BlogApp', '0013_alter_post_time_reading'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='contentimage',
            field=models.ImageField(blank=True, default='PostPic/default.png', null=True, upload_to='PostPic/'),
        ),
    ]
