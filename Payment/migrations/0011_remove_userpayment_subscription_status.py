# Generated by Django 5.0.6 on 2024-06-19 20:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Payment', '0010_remove_userpayment_month_paid_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userpayment',
            name='subscription_status',
        ),
    ]
