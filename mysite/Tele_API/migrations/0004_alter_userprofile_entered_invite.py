# Generated by Django 4.2.1 on 2023-08-17 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Tele_API', '0003_alter_userprofile_entered_invite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='entered_invite',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Tele_API.userprofile'),
        ),
    ]
