# Generated by Django 4.2.18 on 2025-01-31 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0004_delete_individual'),
    ]

    operations = [
        migrations.CreateModel(
            name='Individual',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
    ]
