# Generated by Django 5.1.5 on 2025-02-07 13:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0008_rename_customstyleinvitation_styleinvitation'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StyleInvitation',
            new_name='InvitationStyle',
        ),
    ]
