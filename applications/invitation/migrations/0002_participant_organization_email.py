# Generated by Django 4.2.18 on 2025-02-07 02:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='organization_email',
            field=models.EmailField(blank=True, max_length=254, null=True, validators=[django.core.validators.EmailValidator()], verbose_name='Organization Email'),
        ),
    ]
