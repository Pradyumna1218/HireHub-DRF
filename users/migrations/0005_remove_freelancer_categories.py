# Generated by Django 5.2 on 2025-05-23 06:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_passwordresettoken'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='freelancer',
            name='categories',
        ),
    ]
