# Generated by Django 5.0.6 on 2024-07-21 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alerts', '0021_ema_alert_rsi_alert'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strategy', models.CharField(max_length=50)),
                ('time_frame', models.CharField(max_length=50)),
                ('success', models.IntegerField()),
                ('total', models.IntegerField()),
            ],
        ),
    ]
