# Generated by Django 4.2.18 on 2025-02-13 07:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0026_event_created_by'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='created_by',
            new_name='submitter',
        ),
    ]
