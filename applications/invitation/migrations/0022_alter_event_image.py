# Generated by Django 4.2.18 on 2025-02-12 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0021_remove_invitationstyle_disable_qr_code_invitation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/', verbose_name='Cover Image Event'),
        ),
    ]
