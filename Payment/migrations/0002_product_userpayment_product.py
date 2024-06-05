# Generated by Django 5.0.6 on 2024-06-04 13:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Payment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=17)),
                ('price', models.FloatField()),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='userpayment',
            name='product',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Payment.product'),
        ),
    ]
