# Generated by Django 4.2.18 on 2025-02-17 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0030_alter_participant_approved_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='is_email_sent',
            field=models.BooleanField(default=False),
        ),
    ]
