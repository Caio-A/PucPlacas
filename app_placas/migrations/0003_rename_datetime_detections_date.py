# Generated by Django 4.2.7 on 2023-12-03 00:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_placas', '0002_alter_detections_datetime'),
    ]

    operations = [
        migrations.RenameField(
            model_name='detections',
            old_name='datetime',
            new_name='date',
        ),
    ]
