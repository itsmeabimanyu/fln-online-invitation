# Generated by Django 4.2.18 on 2025-02-18 00:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0033_alter_event_quota_limitation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='quota_limitation',
            field=models.PositiveIntegerField(verbose_name='Participant Quota*'),
        ),
    ]
