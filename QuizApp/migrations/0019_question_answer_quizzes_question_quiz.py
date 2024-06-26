# Generated by Django 5.0.6 on 2024-06-10 12:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuizApp', '0018_remove_question_quiz_remove_quizzes_author_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('technique', models.IntegerField(choices=[(0, 'Multiple Choice')], default=0)),
                ('title', models.CharField(max_length=200)),
                ('difficulty', models.IntegerField(choices=[(0, 'Fundamental'), (1, 'Beginner'), (2, 'Intermediate'), (3, 'Advanced'), (4, 'Expert')], default=0)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=False, verbose_name='Active Status')),
            ],
            options={
                'verbose_name': 'Question',
                'verbose_name_plural': 'Questions',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('answer_text', models.CharField(max_length=200, verbose_name='Answer Text')),
                ('is_right', models.BooleanField(default=False, verbose_name='is_right')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='answer', to='QuizApp.question')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Quizzes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('image', models.ImageField(blank=True, default='QuizPic/default.png', null=True, upload_to='QuizPic/')),
                ('description', models.TextField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('label', models.CharField(blank=True, default=None, max_length=10, null=True)),
                ('duration', models.PositiveIntegerField()),
                ('score', models.PositiveIntegerField()),
                ('achievement', models.PositiveIntegerField(blank=True, null=True)),
                ('likes', models.PositiveIntegerField(blank=True, null=True)),
                ('enrollers', models.PositiveIntegerField(blank=True, null=True)),
                ('questions_counter', models.SmallIntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizzes', to=settings.AUTH_USER_MODEL)),
                ('categories', models.ManyToManyField(to='QuizApp.category')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='question', to='QuizApp.quizzes'),
        ),
    ]
