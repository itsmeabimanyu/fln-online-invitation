# Generated by Django 5.1.5 on 2025-02-03 14:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0014_alter_event_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='description',
        ),
    ]
