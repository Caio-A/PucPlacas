# Generated by Django 4.2.7 on 2023-12-02 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Detections',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ref_img', models.TextField()),
                ('placa', models.TextField()),
                ('datetime', models.DateField()),
            ],
        ),
    ]
