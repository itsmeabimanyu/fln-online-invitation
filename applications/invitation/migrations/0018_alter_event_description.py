# Generated by Django 4.2.19 on 2025-02-09 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0017_alter_event_from_event_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Event Description'),
        ),
    ]
