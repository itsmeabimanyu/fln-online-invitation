# Generated by Django 4.2.18 on 2025-02-13 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0023_alter_event_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='short_link',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True, verbose_name='Short Link'),
        ),
    ]
