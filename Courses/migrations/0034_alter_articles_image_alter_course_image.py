# Generated by Django 5.0.6 on 2024-11-03 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Courses', '0033_remove_questions_course_questions_assessment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articles',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='CoursePic/SectionPic/Default.jpg'),
        ),
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.ImageField(blank=True, default='CoursePic/Default.jpg', null=True, upload_to='CoursePic/'),
        ),
    ]