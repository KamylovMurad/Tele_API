# Generated by Django 4.2.1 on 2023-08-17 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tele_API', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='invite_code_activated',
            field=models.BooleanField(default=False),
        ),
    ]